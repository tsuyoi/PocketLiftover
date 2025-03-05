import os

from liftover import ChainFile


class Lifter:
    def __init__(self, chainfile):
        if not os.path.isfile(chainfile):
            raise FileNotFoundError(f"{chainfile} does not exist")
        self.chain_file = ChainFile(chainfile)

    def liftover_coordinate(self, chrom: str, pos: int) -> (str, int):
        out = self.chain_file[chrom][pos]
        if out is None or len(out) == 0:
            raise ValueError(f"Coordinate {chrom}:{pos} failed to lift over")
        out_chrom = str(out[0][0])
        out_pos = int(out[0][1])
        return out_chrom, out_pos
