"""Central constants for the hackathon demo."""

APP_NAME = "InsightSQL — NL-to-SQL Analytics Agent"
APP_TAGLINE = "Ask in plain English. Get SQL, charts, and business insights."
CURRENCY_LABEL = "Rs"
CURRENCY_SYMBOL = "Rs"

SAMPLE_QUESTIONS = [
    "Show total sales by month",
    "Which product has the highest sales?",
    "Show employee count by department",
    "What is the average salary per department?",
    "Top 5 employees by total sales amount",
    "Sales by product category",
    "List all employees named Priya or Dhana",
    "Which department has the highest total sales?",
    "Show order details for sales in Chennai team",
    "Average unit price by product category",
]

AGENT_STEPS = [
    "Read database schema",
    "Understand user question",
    "Generate SQL",
    "Validate SQL",
    "Execute SQL",
    "Analyze result",
    "Recommend visualization",
]
