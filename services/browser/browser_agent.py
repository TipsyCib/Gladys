from browser_use import Agent, ChatGoogle, Browser
from dotenv import load_dotenv
import sys


load_dotenv()


def run_task(task_description):
    """Exécute une tâche avec Browser Use"""
    browser = Browser()
    agent = Agent(
        task=task_description,
        llm=ChatGoogle(model="gemini-2.5-flash"),
        browser_session=browser
    )
    result = agent.run_sync()
    return result


def execute_browser_task(task_description, expected_result):
        """Exécute une tâche dans le navigateur"""
        print(f"\n🌐 Exécution de la tâche browser...")
        print(f"📋 Tâche: {task_description}")
        print(f"🎯 Résultat attendu: {expected_result}\n")

        # Appeler directement la fonction
        try:
            result = run_task(task_description)

            # Extraire le résultat final
            final_result = "Aucun résultat trouvé"
            if result and hasattr(result, 'final_result'):
                final_result = result.final_result()
            elif result and hasattr(result, 'result'):
                final_result = result.result
            elif result:
                final_result = str(result)

            return {
                "status": "completed",
                "output": final_result,
                "expected_result": expected_result
            }
        except Exception as e:
            return {
                "status": "error",
                "output": str(e),
                "expected_result": expected_result
            }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = sys.argv[1]
        run_task(task)
    else:
        print("Usage: python browser_agent.py 'description de la tâche'")