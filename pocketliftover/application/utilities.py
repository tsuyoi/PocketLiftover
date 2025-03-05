prefix = 'chr'


def toggle_chr_prefix(chrom: str) -> str:
    if chrom.startswith(prefix):
        return chrom[3:]
    return f"{prefix}{chrom}"


def ensure_chr_prefix(chrom: str, has_prefix: bool) -> str:
    if (has_prefix and chrom.startswith(prefix)) or (not has_prefix and not chrom.startswith(prefix)):
        return chrom
    return toggle_chr_prefix(chrom)