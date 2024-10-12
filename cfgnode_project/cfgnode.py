import json
import sys
from collections import defaultdict

class BrilLivenessAnalyzer:
    def __init__(self):
        self.cfg = defaultdict(lambda: {'instrs': [], 'succ': set(), 'pred': set()})
        self.live_in = defaultdict(set)
        self.live_out = defaultdict(set)

    def analyze(self, program):
        for function in program['functions']:
            self.analyze_function(function)

    def analyze_function(self, function):
        self.build_cfg(function['instrs'])
        self.compute_liveness()
        self.print_results()

    def build_cfg(self, instrs):
        self.cfg.clear()
        current_block = 'entry'

        for i, instr in enumerate(instrs):
            if 'label' in instr:
                current_block = instr['label']
            self.cfg[current_block]['instrs'].append(instr)

            if instr.get('op') in ['jmp', 'br']:
                if instr['op'] == 'jmp':
                    target = instr['labels'][0]
                    self.cfg[current_block]['succ'].add(target)
                    self.cfg[target]['pred'].add(current_block)
                elif instr['op'] == 'br':
                    for label in instr['labels']:
                        self.cfg[current_block]['succ'].add(label)
                        self.cfg[label]['pred'].add(current_block)
            elif instr.get('op') == 'ret':
                pass 
            else:
                if i + 1 < len(instrs) and 'label' in instrs[i + 1]:
                    next_block = instrs[i + 1]['label']
                    self.cfg[current_block]['succ'].add(next_block)
                    self.cfg[next_block]['pred'].add(current_block)

    def compute_liveness(self):
        changed = True
        while changed:
            changed = False
            for block in self.cfg:
                old_in = self.live_in[block].copy()
                old_out = self.live_out[block].copy()

                kill = set()
                gen = set()

                for instr in self.cfg[block]['instrs']:
                    if 'dest' in instr:
                        kill.add(instr['dest'])  
                    if 'args' in instr:
                        for arg in instr['args']:
                            if arg not in kill:
                                gen.add(arg)  

                #  OUT{P} = Union of IN{Psuccessor}
                self.live_out[block] = set()
                for succ in self.cfg[block]['succ']:
                    self.live_out[block] |= self.live_in[succ]

                #  IN{P} = (OUT{P} - Kill{P}) U Gen{P}
                self.live_in[block] = (self.live_out[block] - kill) | gen

                if old_in != self.live_in[block] or old_out != self.live_out[block]:
                    changed = True

        self.live_in['entry'] = set()

    def print_results(self):
        for block in self.cfg:
            print(f"Block: {block}")
            print(f"  In:  {sorted(self.live_in[block])}")
            print(f"  Out: {sorted(self.live_out[block])}")
            print()

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            program = json.load(file)
    else:
        program = json.load(sys.stdin)
    
    analyzer = BrilLivenessAnalyzer()
    analyzer.analyze(program)

if __name__ == "__main__":
    main()
