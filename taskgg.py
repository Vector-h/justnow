import os

TASKS_FILE = "tasks.txt"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        lines = f.readlines()
        return [line.strip() for line in lines]

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        for task in tasks:
            f.write(task + "\n")

def display_tasks(tasks):
    if not tasks:
        print("No tasks found.")
    else:
        for i, task in enumerate(tasks):
            print(f"{i + 1}. {task}")

def add_task(tasks):
    task = input("Enter a new task: ")
    tasks.append(task)
    print("Task added.")

def remove_task(tasks):
    display_tasks(tasks)
    try:
        index = int(input("Enter task number to remove: ")) - 1
        removed = tasks.pop(index)
        print(f"Removed: {removed}")
    except (ValueError, IndexError):
        print("Invalid task number.")

def mark_completed(tasks):
    display_tasks(tasks)
    try:
        index = int(input("Enter task number to mark as completed: ")) - 1
        tasks[index] += " [Completed]"
        print("Task marked as completed.")
    except (ValueError, IndexError):
        print("Invalid task number.")

def main():
    tasks = load_tasks()
    while True:
        print("\nTo-Do List Menu:")
        print("1. View Tasks")
        print("2. Add Task")
        print("3. Remove Task")
        print("4. Mark Task as Completed")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            display_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            remove_task(tasks)
        elif choice == "4":
            mark_completed(tasks)
        elif choice == "5":
            save_tasks(tasks)
            print("Tasks saved. Goodbye!")
            break
        else:
            print("Invalid choice.")

main()
