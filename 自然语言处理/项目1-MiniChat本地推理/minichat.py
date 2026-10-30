import argparse
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description='Single-turn local MiniChat inference; not a fine-tuning script')
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--question', required=True)
    p.add_argument('--device', choices=['auto','cpu','cuda'], default='auto')
    p.add_argument('--max-new-tokens', type=int, default=256)
    p.add_argument('--seed', type=int, default=42)
    args=p.parse_args()
    if not args.model.is_dir(): p.error('provide a local model directory including tokenizer and weights')
    if not args.question.strip(): p.error('question must not be empty')
    if args.max_new_tokens < 1: p.error('max-new-tokens must be positive')
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    device=('cuda' if torch.cuda.is_available() else 'cpu') if args.device=='auto' else args.device
    if device=='cuda' and not torch.cuda.is_available(): p.error('CUDA is unavailable')
    dtype=torch.float32 if device=='cpu' else (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16)
    set_seed(args.seed)
    tokenizer=AutoTokenizer.from_pretrained(str(args.model), use_fast=False, local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(str(args.model), torch_dtype=dtype, local_files_only=True).to(device).eval()
    # Uses the model's own template if shipped; fallback preserves the original course prompt.
    if tokenizer.chat_template:
        prompt=tokenizer.apply_chat_template([{'role':'user','content':args.question}], tokenize=False, add_generation_prompt=True)
    else: prompt=f'User: {args.question}\nAssistant:'
    batch=tokenizer(prompt, return_tensors='pt').to(device)
    with torch.inference_mode():
        generated=model.generate(**batch, max_new_tokens=args.max_new_tokens, do_sample=True,
                                 temperature=0.7, pad_token_id=tokenizer.eos_token_id)
    print(tokenizer.decode(generated[0, batch['input_ids'].shape[1]:], skip_special_tokens=True))

if __name__=='__main__': main()
