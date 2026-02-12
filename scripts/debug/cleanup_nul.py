import os

print("Searching for 'nul' file...")
for root, dirs, files in os.walk(os.getcwd()):
    for filename in files:
        if filename.lower() == "nul":
            path = os.path.join(root, filename)
            print(f"Found: {path}")
            try:
                # Try normal remove
                os.remove(path)
                print("Deleted (normal)")
            except:
                try:
                    # Try extended path
                    ext_path = "\\\\?\\" + os.path.abspath(path)
                    print(f"Trying extended path: {ext_path}")
                    os.remove(ext_path)
                    print("Deleted (extended)")
                except Exception as e:
                    print(f"Failed to delete: {e}")
print("Done.")
