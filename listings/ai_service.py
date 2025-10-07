import os
import google.generativeai as genai

def generate_outreach_email(agent):
    """
    Generates a personalized outreach email for a real estate agent.
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        return "ERROR: GOOGLE_API_KEY environment variable not set."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    try:
        stats = agent.agentstats
        
        prompt = f"""
        You are a real estate recruiter writing a concise, personalized, and compelling outreach email to a potential recruit named {agent.agent_name}.

        Here is their data for the last 12 months:
        - Total Sales Volume: ${stats.sales_volume_12mo:,.0f}
        - Total Sides: {stats.sales_count_12mo}
        - Listing Success Rate: {stats.listing_success_rate:.1f}%
        - YoY Volume Change: {stats.yoy_volume_change:.1f}%

        Based on this data, write a 3-paragraph email.
        1. Start with a specific, data-driven compliment about their success.
        2. Briefly introduce a hypothetical value proposition (e.g., better commission splits, superior marketing support, better tech).
        3. End with a clear, low-pressure call to action for a brief, confidential chat.

        The tone should be professional, respectful, and peer-to-peer. Keep it short and impactful. Do not use a subject line.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"An error occurred while generating the email: {e}"
