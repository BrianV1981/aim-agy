import os
import sys
import subprocess
import signal
import time

def get_current_tmux_session():
    current_session = None
    if os.environ.get("TMUX"):
        try:
            result = subprocess.run(["tmux", "display-message", "-p", "#S"], capture_output=True, text=True)
            current_session = result.stdout.strip()
        except Exception:
            pass
    return current_session

def spawn_new_agent(workspace, session_name, wake_up_prompt):
    print("[2/4] Spawning new host vessel (tmux session) with Ephemeral Context Injection...")
    try:
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "-c", workspace, "/home/kingb/.local/bin/agy", "--dangerously-skip-permissions", "-i", wake_up_prompt],
            check=True
        )
        
        # Deterministically handle trust prompt if it appears
        for _ in range(15):
            result = subprocess.run(["tmux", "capture-pane", "-p", "-t", session_name], capture_output=True, text=True)
            if "trust this directory" in result.stdout:
                subprocess.run(["tmux", "send-keys", "-t", session_name, "y"], check=True)
                subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
                break
            time.sleep(0.5)
            
        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except FileNotFoundError:
        print("[ERROR] 'tmux' is not installed. The Reincarnation Protocol requires tmux.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to spawn tmux session: {e}")
        sys.exit(1)
        
    # 3. Native injection handles prompt
    print("[3/4] Wake-up prompt handled natively by Antigravity CLI...")

def execute_teleport(current_session, session_name):
    print("[4/4] Executing Teleport Sequence...")
    
    time.sleep(2)
    
    if os.environ.get("TMUX") and current_session:
        print(f"      [Teleport] TMUX detected. Switching clients from {current_session} to {session_name}...")
        try:
            clients_result = subprocess.run(["tmux", "list-clients", "-t", current_session, "-F", "#{client_name}"], capture_output=True, text=True)
            clients = clients_result.stdout.strip().split("\n")
            
            for client in clients:
                client = client.strip()
                if client:
                    subprocess.run(["tmux", "switch-client", "-c", client, "-t", session_name], check=True)
            
            subprocess.run(["tmux", "kill-session", "-t", current_session])
        except Exception as e:
            print(f"[ERROR] Teleport failed: {e}")
            sys.exit(1)
    else:
        print(f"\n[!] You are not in tmux. To view the new agent, run:\n    tmux attach-session -t {session_name}")
        try:
            input("\nPress Enter to safely exit this session and kill the current agent...")
        except (EOFError, KeyboardInterrupt):
            pass
        parent_pid = os.getppid()
        try:
            os.kill(parent_pid, signal.SIGTERM)
        except Exception as e:
            print(f"[ERROR] Could not self-terminate: {e}")
