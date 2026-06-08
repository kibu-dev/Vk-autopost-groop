from database import init_db
import time

def main():
    init_db()

    print("VK AutoPost Bot started")

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
