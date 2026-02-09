from src.main import KPIAgent

if __name__ == "__main__":
    agent = KPIAgent()
    # Mock URL
    session_id, res, _ = agent.run("s3://bucket/sales_data.csv")
    print(f"Pipeline finished. Session: {session_id}")
    print(res['domain'])
