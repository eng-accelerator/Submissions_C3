from llama_index.core import SimpleDirectoryReader
import os
import pandas as pd

# Create a dummy excel file
df = pd.DataFrame({'Data': [10, 20, 30]})
df.to_excel("test.xlsx", index=False)

try:
    reader = SimpleDirectoryReader(input_files=["test.xlsx"])
    docs = reader.load_data()
    print(f"SUCCESS: Loaded {len(docs)} docs from xlsx")
    print(docs[0].text)
except Exception as e:
    print(f"FAILURE: {e}")
finally:
    if os.path.exists("test.xlsx"):
        os.remove("test.xlsx")
