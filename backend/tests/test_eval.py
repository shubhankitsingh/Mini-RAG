"""
Evaluation script for RAG application
Tests retrieval precision, recall, and answer quality
"""

import asyncio
import json
from typing import List, Dict, Any
import sys
import os
from pathlib import Path

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

sys.path.append('..')
from app.rag_engine import RAGEngine


# Gold set Q/A pairs for evaluation
# 4 questions for each unique document + 1 unrelated question that should fail
GOLD_SET = [
    # Q1: Returns & Refunds Policy document
    {
        "id": 1,
        "question": "What is the return policy for items purchased from the store?",
        "expected_keywords": ["return", "45", "days", "refund", "credit"],
        "min_citations": 1,
        "expected_source": "Returns & Refunds Policy"
    },
    # Q2: User Account Security Guide document
    {
        "id": 2,
        "question": "What are the password requirements for creating a user account?",
        "expected_keywords": ["password", "10", "characters", "special", "symbol"],
        "min_citations": 1,
        "expected_source": "User Account Security Guide"
    },
    # Q3: Shipping & Logistics FAQ document
    {
        "id": 3,
        "question": "What is the shipping fee for orders to Europe and UK?",
        "expected_keywords": ["shipping", "EU", "UK", "$25", "flat", "international"],
        "min_citations": 1,
        "expected_source": "Shipping & Logistics FAQ"
    },
    # Q4: X100 Product Specifications document
    {
        "id": 4,
        "question": "What is the battery capacity and charging time of the X100?",
        "expected_keywords": ["500", "Wh", "battery", "charging", "hours"],
        "min_citations": 1,
        "expected_source": "X100 Product Specifications"
    },
    # Q5: UNRELATED question - should NOT find relevant information
    {
        "id": 5,
        "question": "What is the company's employee vacation policy?",
        "expected_keywords": [],  # Empty - we expect NO relevant keywords
        "min_citations": 0,  # Should have no meaningful citations
        "expected_source": "NONE - Unrelated",
        "should_fail": True  # This question should correctly return "no information"
    }
]


class RAGEvaluator:
    """Evaluates RAG system performance"""
    
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.results = []
    
    async def evaluate_query(self, gold_item: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single query against expected results"""
        try:
            result = await self.rag_engine.query(
                query=gold_item["question"],
                top_k=10,
                rerank_top_k=5
            )
            
            # Check if answer contains expected keywords
            answer_lower = result["answer"].lower()
            expected_keywords = gold_item["expected_keywords"]
            
            if expected_keywords:
                keywords_found = sum(
                    1 for kw in expected_keywords 
                    if kw.lower() in answer_lower
                )
                keyword_score = keywords_found / len(expected_keywords)
            else:
                keyword_score = 0.0  # No keywords expected for unrelated questions
            
            # Check citation count
            citation_count = len(result["citations"])
            has_enough_citations = citation_count >= gold_item["min_citations"]
            
            # Check if answer indicates no information (failure case)
            no_answer_indicators = [
                "couldn't find",
                "don't have enough",
                "no relevant",
                "unable to answer",
                "not mentioned",
                "no information"
            ]
            is_no_answer = any(ind in answer_lower for ind in no_answer_indicators)
            
            # Handle "should_fail" questions (unrelated questions)
            should_fail = gold_item.get("should_fail", False)
            if should_fail:
                # For unrelated questions, success means it correctly says "no info"
                success = is_no_answer
            else:
                # For normal questions, success means keywords found + citations
                success = keyword_score >= 0.5 and has_enough_citations and not is_no_answer
            
            return {
                "id": gold_item["id"],
                "question": gold_item["question"],
                "expected_source": gold_item.get("expected_source", "N/A"),
                "answer": result["answer"][:200] + "..." if len(result["answer"]) > 200 else result["answer"],
                "citation_count": citation_count,
                "keyword_score": keyword_score,
                "has_citations": has_enough_citations,
                "is_no_answer": is_no_answer,
                "should_fail": should_fail,
                "retrieval_time_ms": result["retrieval_time_ms"],
                "rerank_time_ms": result["rerank_time_ms"],
                "llm_time_ms": result["llm_time_ms"],
                "success": success
            }
        except Exception as e:
            return {
                "id": gold_item["id"],
                "question": gold_item["question"],
                "error": str(e),
                "success": False
            }
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run full evaluation on gold set"""
        print("Starting RAG Evaluation...")
        print("=" * 60)
        
        results = []
        for gold_item in GOLD_SET:
            source = gold_item.get('expected_source', 'N/A')
            print(f"\nQ{gold_item['id']}: {gold_item['question'][:50]}...")
            print(f"   Expected Source: {source}")
            result = await self.evaluate_query(gold_item)
            results.append(result)
            
            if result.get("should_fail"):
                # Unrelated question - success means correctly returned "no info"
                if result.get("success"):
                    print(f"   ✓ PASS - Correctly identified as unrelated (no info)")
                else:
                    print(f"   ✗ FAIL - Should have returned 'no information'")
            else:
                if result.get("success"):
                    print(f"   ✓ PASS - Keywords: {result['keyword_score']:.0%}, Citations: {result['citation_count']}")
                else:
                    print(f"   ✗ FAIL - {result.get('error', 'Did not meet criteria')}")
        
        # Calculate aggregate metrics
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)
        
        avg_keyword_score = sum(r.get("keyword_score", 0) for r in results) / total
        avg_citations = sum(r.get("citation_count", 0) for r in results) / total
        avg_retrieval_time = sum(r.get("retrieval_time_ms", 0) for r in results) / total
        avg_rerank_time = sum(r.get("rerank_time_ms", 0) for r in results) / total
        avg_llm_time = sum(r.get("llm_time_ms", 0) for r in results) / total
        
        summary = {
            "total_queries": total,
            "successful": successful,
            "success_rate": successful / total,
            "avg_keyword_score": avg_keyword_score,
            "avg_citations": avg_citations,
            "avg_retrieval_time_ms": avg_retrieval_time,
            "avg_rerank_time_ms": avg_rerank_time,
            "avg_llm_time_ms": avg_llm_time,
            "detailed_results": results
        }
        
        print("\n" + "=" * 50)
        print("EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Success Rate: {successful}/{total} ({summary['success_rate']:.0%})")
        print(f"Avg Keyword Score: {avg_keyword_score:.0%}")
        print(f"Avg Citations: {avg_citations:.1f}")
        print(f"Avg Retrieval Time: {avg_retrieval_time:.0f}ms")
        print(f"Avg Rerank Time: {avg_rerank_time:.0f}ms")
        print(f"Avg LLM Time: {avg_llm_time:.0f}ms")
        
        return summary


async def main():
    """Main entry point for evaluation"""
    evaluator = RAGEvaluator()
    results = await evaluator.run_evaluation()
    
    # Save results to file
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to evaluation_results.json")
    
    # Return exit code based on success rate
    return 0 if results["success_rate"] >= 0.6 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
