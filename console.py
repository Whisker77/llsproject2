from langchain_core.tools import StructuredTool

def search_fun(query: str):
    return "最后的查询结果"

search_tool = StructuredTool.from_function(
 func=search_fun,
 name="Search",
 description="从Google搜索引擎进行查询"
)

print(f"name={search_tool.name}")
print(f"args={search_tool.args}")
print(f"desciption={search_tool.description}")

search_tool.invoke("查询")