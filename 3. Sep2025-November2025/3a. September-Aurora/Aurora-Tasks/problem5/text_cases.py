import json
from typing import Dict, List, Any

from IR import optimize_allocation

def run_public_test_cases():
    
    public_test_cases = [
        {
            "input": "{\"graph\": {\"1\": [2, 3], \"2\": [1, 4, 5], \"3\": [1, 5], \"4\": [2, 5], \"5\": [2, 3, 4]}, \"room_availability\": {\"1\": true, \"2\": true, \"3\": false, \"4\": true, \"5\": true}, \"guest_preferences\": {\"101\": [2, 5], \"102\": [1, 3], \"103\": [4], \"104\": [2, 3, 5]}, \"logistical_constraints\": {\"corridor_capacity\": {\"(2, 5)\": 2}, \"maintenance_times\": {\"3\": [10, 14]}, \"preferred_floor\": 2, \"overlap_threshold\": 2}}",
            "output": "{\"101\": 2, \"102\": 1, \"103\": 4, \"104\": 5}",
            "testtype": "stdin"
        },
        {
            "input": "{\"graph\": {\"1\": [2], \"2\": [1, 3], \"3\": [2]}, \"room_availability\": {\"1\": true, \"2\": true, \"3\": true}, \"guest_preferences\": {\"201\": [1], \"202\": [2]}, \"logistical_constraints\": {\"overlap_threshold\": 1, \"max_group_distance\": 50.0}}",
            "output": "{\"201\": 1, \"202\": 2}",
            "testtype": "stdin"
        },
        {
            "input": "{\"graph\": {\"1\": [2, 3], \"2\": [1, 3], \"3\": [1, 2]}, \"room_availability\": {\"1\": true, \"2\": true, \"3\": true}, \"guest_preferences\": {\"301\": [1, 2], \"302\": [2, 3], \"303\": [1, 3]}, \"logistical_constraints\": {\"corridor_capacity\": {\"(1, 2)\": 3}, \"overlap_threshold\": 2}}",
            "output": "{\"301\": 1, \"302\": 2, \"303\": 3}",
            "testtype": "stdin"
        }
    ]
    
    print("Running Public Test Cases for optimize_allocation function")
    print("=" * 70)
    
    total_tests = len(public_test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(public_test_cases, 1):
        print(f"\nPublic Test Case {i}:")
        print("-" * 30)
        
        try:
            # Parse input JSON string
            input_data = json.loads(test_case["input"])
            
            # Convert string keys to integers for graph and room_availability
            graph = {int(k): v for k, v in input_data["graph"].items()}
            room_availability = {int(k): v for k, v in input_data["room_availability"].items()}
            guest_preferences = {int(k): v for k, v in input_data["guest_preferences"].items()}
            logistical_constraints = input_data["logistical_constraints"]
            
            # Convert corridor capacity keys from string tuples to actual tuples
            if "corridor_capacity" in logistical_constraints:
                corridor_capacity = {}
                for k, v in logistical_constraints["corridor_capacity"].items():
                    # Parse string tuple like "(2, 5)" to actual tuple (2, 5)
                    key_tuple = eval(k)
                    corridor_capacity[key_tuple] = v
                logistical_constraints["corridor_capacity"] = corridor_capacity
            
            # Parse expected output
            expected_output = json.loads(test_case["output"])
            expected_output = {int(k): v for k, v in expected_output.items()}
            
            # Call the optimize_allocation function
            actual_output = optimize_allocation(graph, room_availability, guest_preferences, logistical_constraints)
            
            # Compare results
            test_passed = actual_output == expected_output
            if test_passed:
                passed_tests += 1
            
            # Display results
            print(f"Input Graph: {graph}")
            print(f"Room Availability: {room_availability}")
            print(f"Guest Preferences: {guest_preferences}")
            print(f"Constraints: {logistical_constraints}")
            print(f"Expected Output: {expected_output}")
            print(f"Actual Output:   {actual_output}")
            print(f"Test Result: {'PASS' if test_passed else 'FAIL'}")
            
            if not test_passed:
                print("Differences found:")
                all_guests = set(list(expected_output.keys()) + list(actual_output.keys()))
                for guest in all_guests:
                    expected_room = expected_output.get(guest, "Not allocated")
                    actual_room = actual_output.get(guest, "Not allocated")
                    if expected_room != actual_room:
                        print(f"  Guest {guest}: Expected room {expected_room}, Got room {actual_room}")
        
        except Exception as e:
            print(f"ERROR during test execution: {str(e)}")
            print(f"Test Result: FAIL (Exception)")
    
    # Summary
    print("\n" + "=" * 70)
    print("PUBLIC TEST SUMMARY:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Failed Tests: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("All public test cases PASSED!")
    else:
        print("Some public test cases FAILED. Please check the implementation.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run the main public test function
    success = run_public_test_cases()
    
    # Final status
    print("\n" + "=" * 70)
    if success:
        print("All public test cases completed successfully!")
    else:
        print("Some public test cases failed!")