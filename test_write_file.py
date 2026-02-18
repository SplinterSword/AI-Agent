from functions.write_file import write_file

print("Testing write_file function...")
result1 = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
print(result1)
print("First write completed")
print()

result2 = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
print(result2)
print("Second write completed")
print()

result3 = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
print(result3)
print("Third write completed (should show error)")
print("All tests completed!")
