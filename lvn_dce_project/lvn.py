import json
import sys

def lvn(func):
    new_instrs = []
    value_table = {}  
    var_table = {}   

    for instr in func['instrs']:
        if 'op' in instr:
            if instr['op'] == 'const':
                value = instr['value']
                value_num = get_value_number(value_table, ('const', value))
                value_table[value_num] = ('const', value, instr['dest'])
                var_table[instr['dest']] = value_num
                new_instrs.append(instr)
            elif instr['op'] == 'print':
                new_instr = instr.copy()
                if 'args' in new_instr:
                    new_instr['args'] = [value_table[var_table[arg]][2] for arg in new_instr['args']]
                new_instrs.append(new_instr)
            else:
                args = [var_table.get(arg, arg) for arg in instr.get('args', [])]
                value_num = get_value_number(value_table, (instr['op'], tuple(args)))

                if value_num in value_table:
                    # Redundant computation found here!
                    canonical_op, canonical_args, canonical_var = value_table[value_num]
                    var_table[instr['dest']] = value_num
                else:
                    new_instr = instr.copy()
                    new_instr['args'] = [value_table[arg][2] if arg in value_table else arg for arg in args]
                    value_table[value_num] = (instr['op'], tuple(args), instr['dest'])
                    var_table[instr['dest']] = value_num
                    new_instrs.append(new_instr)
        else:
            new_instrs.append(instr)

    func['instrs'] = new_instrs
    return func

def get_value_number(value_table, key):
    for num, (op, args, var) in value_table.items():
        if op == key[0] and args == key[1]:
            return num
    return len(value_table)

def main():
    try:
        bril_input = json.load(sys.stdin)
        for func in bril_input['functions']:
            lvn(func)
        json.dump(bril_input, sys.stdout, indent=2)
        sys.stdout.flush()
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()