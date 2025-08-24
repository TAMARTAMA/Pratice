

from typing import List, Dict, Tuple, Optional


from Game.Command import Command

from Game.Piece   import Piece
def _side_of( piece_id: str) -> str:
        """
        Return 'W' or 'B' from an id formatted like 'PW_(6,1)'.
        Second character after the initial type letter is the colour.
        """
        return piece_id[1] 

def _path_is_clear( a, b, pos):
    ar, ac = a
    br, bc = b
    dr = (br - ar) and ((br - ar) // abs(br - ar))
    dc = (bc - ac) and ((bc - ac) // abs(bc - ac))
    r, c = ar + dr, ac + dc
    while (r, c) != (br, bc):
        if (r, c) in pos:
            return False
        r, c = r + dr, c + dc
    return True

def _process_input_client( cmd: Command,piece_by_id,time_ms,pos):
    mover = piece_by_id.get(cmd.piece_id)
    if not mover:
        print(f"[DBG] unknown piece id {cmd.piece_id}")
        return

    now_ms = time_ms

    current_state = mover.state.name
    if current_state == "long_rest" or current_state == "short_rest" :
        return

    candidate_state = mover.state.transitions.get(cmd.type, mover.state)
    moveset = candidate_state.moves  

    src = mover.state.physics.start_cell
    dest = cmd.params[0]

    legal_offset = dest in moveset.get_moves(*src)

    piece_type = mover.id[0]
    if piece_type == "P":
        direction = -1 if mover.id[1] == "W" else 1  
        is_end = 0 if mover.id[1] == "W" else 7  
        dr, dc = dest[0] - src[0], dest[1] - src[1]

        forward_move = dr == direction and dc == 0
        diagonal_move = dr == direction and abs(dc) == 1
        occupant = pos.get(dest)
        
        if forward_move:
            legal_offset = legal_offset and occupant is None
        elif diagonal_move:
            legal_offset = legal_offset and occupant is not None and occupant.id[1] != mover.id[1]
        else:
            legal_offset = False
        if legal_offset and is_end == dest[0]:
            change_pwan_to_queen(mover,cmd)
    occupant = pos.get(dest)
    friendly_block = (
        occupant is not None and
        occupant.state.name is not "jump" and
        occupant is not mover and
        occupant.id[1] == mover.id[1]
    )

    path_clear = True
    if mover.id[0] in ("R", "B", "Q"):  
        path_clear = _path_is_clear(src, dest)

    print(f"[DBG] {cmd.type} {src}->{dest}  "
        f"offset_ok={legal_offset}  friend={friendly_block}  clear={path_clear}")

    if legal_offset and path_clear and not friendly_block:

        if occupant is not None:
            player_color = "white" if mover.id[1] == "W" else "black"
            
            occupant.state.physics.captured()
            mover.state.physics.in_captured("piece_captured_"+mover.id[1],{"by":player_color,"piece":occupant},cmd)
        else:
            mover.state.physics.add_history("piece_moved_"+mover.id[1],cmd)
        mover.state = candidate_state
        mover.state.reset(cmd)  
        
        print(f"[EXEC] {mover.id} performs {cmd.type}")


    else:
        mover.state.reset(Command(now_ms, mover.id, "idle", []))
        print("[FAIL] move rejected")

def _process_input( cmd: Command,piece_by_id,time_ms,pos):
    mover = piece_by_id.get(cmd.piece_id)
    if not mover:
        print(f"[DBG] unknown piece id {cmd.piece_id}")
        return

    now_ms = time_ms

    current_state = mover.state.name
    if current_state == "long_rest" or current_state == "short_rest" :
        return

    candidate_state = mover.state.transitions.get(cmd.type, mover.state)
    moveset = candidate_state.moves  

    src = mover.state.physics.start_cell
    dest = cmd.params[0]

    legal_offset = dest in moveset.get_moves(*src)

    piece_type = mover.id[0]
    if piece_type == "P":
        direction = -1 if mover.id[1] == "W" else 1  
        is_end = 0 if mover.id[1] == "W" else 7  
        dr, dc = dest[0] - src[0], dest[1] - src[1]

        forward_move = dr == direction and dc == 0
        diagonal_move = dr == direction and abs(dc) == 1
        occupant = pos.get(dest)
        
        if forward_move:
            legal_offset = legal_offset and occupant is None
        elif diagonal_move:
            legal_offset = legal_offset and occupant is not None and occupant.id[1] != mover.id[1]
        else:
            legal_offset = False
        if legal_offset and is_end == dest[0]:
            change_pwan_to_queen(mover,cmd)
    occupant = pos.get(dest)
    friendly_block = (
        occupant is not None and
        occupant.state.name is not "jump" and
        occupant is not mover and
        occupant.id[1] == mover.id[1]
    )

    path_clear = True
    if mover.id[0] in ("R", "B", "Q"):  
        path_clear = _path_is_clear(src, dest)

    print(f"[DBG] {cmd.type} {src}->{dest}  "
        f"offset_ok={legal_offset}  friend={friendly_block}  clear={path_clear}")

    if legal_offset and path_clear and not friendly_block:

        if occupant is not None:
            player_color = "white" if mover.id[1] == "W" else "black"
            
            occupant.state.physics.captured()
            mover.state.physics.in_captured("piece_captured_"+mover.id[1],{"by":player_color,"piece":occupant},cmd)
        else:
            mover.state.physics.add_history("piece_moved_"+mover.id[1],cmd)
        mover.state = candidate_state
        mover.state.reset(cmd)  
        
        print(f"[EXEC] {mover.id} performs {cmd.type}")


    else:
        mover.state.reset(Command(now_ms, mover.id, "idle", []))
        print("[FAIL] move rejected")


def _resolve_collisions(pieces):
    occupied: Dict[Tuple[int, int], List[Piece]] = {}
    for p in pieces:
        cell = p.state.physics.start_cell
        occupied.setdefault(cell, []).append(p)

    for cell, plist in occupied.items():
        if len(plist) < 2:
            continue

        winner = max(plist, key=lambda pc: pc.state.physics.start_ms)

        for p in plist:
            if p is not winner and p.state.physics.can_be_captured():
                pieces.remove(p)

def _validate( pieces: List[Piece]) -> bool:
    seen_cells = set()
    has_white_king = has_black_king = False
    for p in pieces:
        cell = p.state.physics.start_cell
        if cell in seen_cells:
            return False
        seen_cells.add(cell)
        if p.id.startswith("KW"): has_white_king = True
        if p.id.startswith("KB"): has_black_king  = True
    return has_white_king and has_black_king

def _is_win(pieces) -> bool:
    return sum(p.id.startswith("K") for p in pieces) < 2


        

def _announce_win(pieces):
    
    if any(p.id.startswith("KB") for p in pieces) and any(p.id.startswith("KW") for p in pieces):
        text = "Exit Game!"
    elif  not any(p.id.startswith("KB") for p in pieces) :
        text = "White wins!"
    else:
        text ="Black wins!"
    return text
def change_pwan_to_queen(piece:Piece,cmd:Command,pf,pieces):
    if piece is None:
        return
    color = _side_of(piece.id) 
    current_cell = cmd.params[0]
    new_piece_queen =pf.create_piece("Q"+color,current_cell)
    for i in range(len(pieces)):
        if pieces[i] is piece:
            pieces[i] = new_piece_queen
        