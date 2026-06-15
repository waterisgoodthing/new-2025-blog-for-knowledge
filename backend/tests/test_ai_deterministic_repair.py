import unittest

from app.routers.ai import _repair_deterministic_result


class DeterministicRepairTest(unittest.IsolatedAsyncioTestCase):
    async def test_repairs_hedged_final_fields_with_model_result(self):
        original = {
            "title": "IPv4分片计算题",
            "question": "求第2个分片总长度和MF。",
            "correct_answer": "总长度：800B，MF=1",
            "analysis": "根据8字节对齐，答案可能是796B，也可能按教材写800B。",
            "error_reason": "",
            "key_step": "",
        }
        repaired_payload = {
            **original,
            "correct_answer": "总长度：796B，MF=1",
            "analysis": "数据载荷为1580-20=1560B。每片最大载荷为800-20=780B，除最后一片外必须按8B对齐，因此最大合法载荷为776B。第1片载荷776B后剩余784B；第2片载荷776B，总长度为776+20=796B，后续仍有8B数据，所以MF=1。",
        }
        calls = []

        async def fake_model(messages, max_tokens=4000):
            calls.append((messages, max_tokens))
            return repaired_payload

        repaired, warnings = await _repair_deterministic_result(original, fake_model)

        self.assertEqual(repaired["correct_answer"], "总长度：796B，MF=1")
        self.assertNotIn("可能", repaired["analysis"])
        self.assertEqual(warnings, [])
        self.assertEqual(len(calls), 1)
        self.assertIn("不得使用", calls[0][0][0]["content"])


if __name__ == "__main__":
    unittest.main()
