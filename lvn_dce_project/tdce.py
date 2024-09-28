import json
import sys

def tdce(func):
    used_vars = set()
    instructions = func['instrs']
    new_instructions = []

    for instr in reversed(instructions):
        if 'dest' in instr:
            if instr['dest'] not in used_vars:
                continue  #skip this instruction as its destination is never used
            used_vars.remove(instr['dest'])
        
        if 'args' in instr:
            used_vars.update(instr['args'])
        
        new_instructions.append(instr)
    
    func['instrs'] = list(reversed(new_instructions))
    return func

def main():
    prog = json.load(sys.stdin)
    
    for func in prog['functions']:
        func = tdce(func)
    
    json.dump(prog, sys.stdout, indent=2)

if __name__ == "__main__":
    main()