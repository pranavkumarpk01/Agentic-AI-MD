from workflows.sequential_flow import  sequential_flow
from workflows.parallel_flow import  parallel_execute
from workflows.supervisor_flow import supervisor_execute


print("\n1. Sequential Flow")
print("2. Parallel Flow")
print("3. Supervisor Flow")

choice = input("\nChoose Demo: ")

if choice == "1":

    result = sequential_flow(
        "Future of Artificial Intelligence"
    )

    print(result)

elif choice == "2":

    result = parallel_execute(
        "Microsoft"
    )

    print(result)

elif choice == "3":

    result = supervisor_execute(
        "want to go to Paris next month"
    )

    print(result)

else:
    print("Invalid Choice")