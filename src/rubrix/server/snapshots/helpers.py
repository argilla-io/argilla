import mmap
from typing import Optional

import numpy as np
from fastapi.responses import StreamingResponse


def stream_from_uri(uri: str, limit: Optional[int] = None) -> StreamingResponse:
    """
    Stream data file as streaming response

    Parameters
    ----------
    uri:
        The file uri
    limit:
        The number of lines to read. Optional

    Returns
    -------
        An StreamingResponse for uri data streaming

    """

    uri = uri.replace("file://", "")  # TODO: generalize uri to path
    media_type = "application/json"  # TODO: inferred from uri

    def scan_offsets():
        """
        Scan file to find byte offsets
        """
        tmp_offsets = [0]
        eof_symbol = b""
        with open(uri, "r+b") as f:
            mm = mmap.mmap(
                f.fileno(), 0, access=mmap.ACCESS_READ
            )  # lazy eval-on-demand via POSIX filesystem
            for _ in iter(mm.readline, eof_symbol):
                pos = mm.tell()
                tmp_offsets.append(pos)

        tmp_offsets = tmp_offsets[:limit] if limit else tmp_offsets
        # convert to numpy array for compactness;
        # can use uint32 for small and medium corpora (i.e., less than 100M lines)
        offsets = np.asarray(tmp_offsets, dtype="uint64")
        return offsets

    def iterator():
        """Iterate over uri data"""
        offsets = scan_offsets()
        with open(uri, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            len_offsets = len(offsets)  # compute once
            for line_number, offset in enumerate(offsets):  # traverse random path
                if int(line_number) >= len_offsets:
                    # print("Error at line number: %d" % line_number)
                    continue
                offset_begin = offsets[line_number]
                try:
                    mm.seek(offset_begin)
                    line = mm.readline()
                except:
                    # print("Error at location: %d" % offset)
                    continue
                if len(line) == 0:
                    continue  # no point to returning an empty list (i.e., whitespace)
                yield line

    return StreamingResponse(iterator(), media_type=media_type)
