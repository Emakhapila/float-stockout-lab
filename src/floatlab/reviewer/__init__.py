"""AI reviewer: audits an experiment with read-only tools and drafts the memo.

The statistics are deterministic code in floatlab.experiment; the LLM only
orchestrates, interprets and writes. It never makes the ship decision.
"""
