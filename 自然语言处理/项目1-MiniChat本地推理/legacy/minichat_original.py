import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载tokenizer和模型
tokenizer = AutoTokenizer.from_pretrained("./minichat-2-3b", use_fast=False)
model = AutoModelForCausalLM.from_pretrained(
    "./minichat-2-3b", use_cache=True, device_map="auto", torch_dtype=torch.bfloat16
).eval()

# 用户输入问题
question = "Solve for x: 5x + 3 = 29."

# 将用户输入转换为模型输入
input_text = f"User: {question}\nAssistant:"
input_ids = tokenizer.encode(input_text, return_tensors="pt").cuda()

# 进行推理
output_ids = model.generate(
    input_ids,
    do_sample=True,
    temperature=0.7,
    max_new_tokens=1024,
)

# 提取生成的答案并解码
output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

# 输出结果
print(f"模型生成的答案是: {output_text}")
