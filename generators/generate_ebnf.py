"""Generator routine for a grammar written in EBNF"""
import time
from argparse import ArgumentParser
from pathlib import Path

from derp.ast import to_string
from derp.parsers import parse
from ebnf.generate import ParserGenerator
from ebnf.meta_grammar import b
from ebnf.tokenizer import tokenize_file

if __name__ == "__main__":
    parser = ArgumentParser(description='BNF parser generator')
    parser.add_argument('--grammar_filepath', default="sample.ebnf", type=Path)
    args = parser.parse_args()

    tokens = list(tokenize_file(args.grammar_filepath))
    print("Parsing BNF grammar: {} with {} tokens".format(args.grammar_filepath, len(tokens)))

    start_time = time.monotonic()
    result = parse(b.grammar, tokens)
    finish_time = time.monotonic()

    if not result:
        print("Failed to parse BNF")

    elif len(result) > 1:
        print("Ambiguous parse of BNF, mutliple parse trees")

    else:
        root = result.pop()
        print("==========Built AST============")
        print(to_string(root))
        #
        # Generate parsers from AST
        generator = ParserGenerator(name='EBNF', variable='e')
        grammar = generator.visit(root)

        print("==========Built Grammar============")
        print(grammar)