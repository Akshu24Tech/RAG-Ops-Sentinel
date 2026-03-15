import phoenix as px
import time

try:
    print("Attempting to launch Phoenix...")
    session = px.launch_app()
    print(f"Phoenix launched successfully!")
    print(f"URL: {session.url}")
    print("Keeping session alive for 30s...")
    time.sleep(30)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
