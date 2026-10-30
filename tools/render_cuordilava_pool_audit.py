#!/usr/bin/env python3
"""Small self-contained real-pixel diagnostic for the original thermal pool.

Read the two actual 960x960 RGB render outputs, crop precisely the same
9x8 original Lavaridge Town map-cell rectangle, then highlight the four
EXTERIOR bank cells that once displayed erroneous waterfalls. This is an
annotated audit image, not a new in-game tile or a source-art modification.
Uses Python standard library only; no Pillow on the Actions runners.
"""
from pathlib import Path
import argparse
import json
import struct
import zlib

CELL_PX = 48  # 20 map cells x 48 -> native 960px preview
TOWN_SIZE = 20
REGION = (0, 1, 9, 9)  # x0,y0,x1,y1 in actual world cells
EXTERIOR = ((1, 4), (2, 4), (1, 5), (2, 5))
INSIDE = ((3, 3), (4, 3), (5, 3), (6, 3),
          (3, 4), (4, 4), (5, 4), (6, 4),
          (3, 5), (4, 5), (5, 5), (6, 5))


def chunk(kind, body):
    return (
        struct.pack('>I', len(body)) + kind + body
        + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff)
    )


def read_preview(path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: invalid preview signature')
    pos = 8
    payload = bytearray()
    dimensions = None
    while pos < len(data):
        length = struct.unpack_from('>I', data, pos)[0]
        kind = data[pos+4:pos+8]
        body = data[pos+8:pos+8+length]
        if len(body) != length:
            raise ValueError(f'{path}: truncated chunk')
        if struct.unpack_from('>I', data, pos+8+length)[0] != zlib.crc32(kind+body)&0xffffffff:
            raise ValueError(f'{path}: CRC mismatch')
        pos += length+12
        if kind == b'IHDR':
            w,h,bits,rgb,compression,filtering,interlace = struct.unpack('>IIBBBBB',body)
            if (w,h,bits,rgb,compression,filtering,interlace) != (960,960,8,2,0,0,0):
                raise ValueError(f'{path}: unexpected non-RGB map preview')
            dimensions = (w,h)
        if kind == b'IDAT':
            payload.extend(body)
        if kind == b'IEND':
            break
    if dimensions is None:
        raise ValueError(f'{path}: missing header')
    raw = zlib.decompress(payload)
    width, height = dimensions
    stride = width * 3
    if len(raw) != (stride + 1) * height:
        raise ValueError(f'{path}: damaged preview pixel length')
    rows = []
    for y in range(height):
        start = y * (stride + 1)
        if raw[start] != 0:  # pack_png uses raw scanline filter 0
            raise ValueError(f'{path}: preview must use unfiltered RGB')
        rows.append(raw[start+1:start+1+stride])
    return rows


def crop_with_bank_outline(rows):
    x0,y0,x1,y1 = REGION
    xpx,ypx = x0*CELL_PX,y0*CELL_PX
    width,height = (x1-x0)*CELL_PX,(y1-y0)*CELL_PX
    image = bytearray()
    for y in range(ypx, ypx+height):
        image.extend(rows[y][xpx*3:(xpx+width)*3])
    # This gold outline marks the *audited exterior bank*, not a new in-game
    # graphic. It must remain four unaltered original map cells.
    edge = (229, 177, 80)
    for cx,cy in EXTERIOR:
        left = (cx-x0)*CELL_PX
        top = (cy-y0)*CELL_PX
        for d in range(CELL_PX):
            for xx,yy in ((left+d, top), (left+d, top+CELL_PX-1),
                          (left, top+d), (left+CELL_PX-1, top+d)):
                idx=(yy*width+xx)*3
                image[idx:idx+3]=bytes(edge)
    return width,height,image


def write_png(path,w,h,flat):
    scans=bytearray()
    for y in range(h):
        scans.append(0)
        scans.extend(flat[y*w*3:(y+1)*w*3])
    image = (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
        + chunk(b'IDAT',zlib.compress(bytes(scans),9))
        + chunk(b'IEND',b'')
    )
    path.write_bytes(image)


def run(input_dir,output_dir):
    output_dir.mkdir(parents=True,exist_ok=True)
    results={}
    for mode in ('day','night'):
        source=input_dir/f'cuordilava-{mode}.png'
        w,h,pix=crop_with_bank_outline(read_preview(source))
        out=output_dir/f'cuordilava-thermal-perimeter-{mode}.png'
        write_png(out,w,h,pix)
        results[mode]={'file':out.name,'width':w,'height':h,'bytes':out.stat().st_size}
        if out.stat().st_size < 1000:
            raise ValueError('Thermal pool diagnostic is unexpectedly empty')
    data={
        'purpose':'Check original exterior bank for water spilling beyond the thermal pool',
        'diagnostic_only':True,
        'gold_outline':'Four original exterior bank cells; not in-game art',
        'map_dimensions':[TOWN_SIZE,TOWN_SIZE],
        'region_cells':[list(REGION[:2]),list(REGION[2:])],
        'exterior_bank_cells':list(map(list,EXTERIOR)),
        'pool_inner_cells':list(map(list,INSIDE)),
        'outputs':results,
    }
    (output_dir/'cuordilava-thermal-perimeter.json').write_text(
        json.dumps(data,indent=2)+'\n',encoding='utf-8'
    )
    print('Thermal pool: daytime/nighttime close-up with four exterior bank cells marked')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input-dir',type=Path,default=Path('build-preview'))
    parser.add_argument('--output-dir',type=Path,default=Path('build-preview'))
    args=parser.parse_args()
    run(args.input_dir,args.output_dir)
