#!/usr/bin/env python3
"""
validate.py — replays a Fly-in simulation's printed output against its map
file and checks whether zone capacities, connection capacities, and
connectivity were respected at every turn.

USAGE:
    p main.py maps/xxx.txt > output.txt
    python3 validate.py maps/xxx.txt output.txt

    or pipe directly:
    p main.py maps/xxx.txt | python3 validate.py maps/xxx.txt -

WHAT IT CHECKS:
    1. Every move is between two zones that actually have a connection
       in the map (no teleporting).
    2. No zone ever holds more drones than its max_drones capacity at
       the moment a drone arrives there.
    3. No connection has more drones crossing it in a single turn than
       its max_link_capacity.
    4. Every drone eventually reaches the end_hub.

KNOWN LIMITATION:
    Restricted zones take 2 turns to cross (enter, then arrive next turn).
    This script checks connection capacity based on same-turn crossings
    only — it does not model a drone "occupying" a connection across its
    full 2-turn transit window. If your restricted connections have
    max_link_capacity=1 and two drones could start transiting in
    consecutive turns, that overlap is NOT flagged. Treat this as a
    same-turn sanity check, not an absolute proof of correctness.
"""
import sys
from collections import defaultdict


class MapError(Exception):
    pass


def parse_map(path):
    zones = {}          # name -> dict(capacity, zone_type)
    connections = set()  # frozenset({a, b}) -> capacity, stored separately
    conn_capacity = {}
    start_name = None
    end_name = None
    nb_drones = None

    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones"):
                nb_drones = int(line.split()[1])

            elif line.startswith(("start_hub", "end_hub", "hub")):
                parts = line.split()
                # parts[0] is "start_hub:"/"end_hub:"/"hub:"
                name = parts[1]
                capacity = 1
                zone_type = "normal"
                if "[" in line:
                    inside = line[line.find("[") + 1:line.find("]")]
                    for kv in inside.split():
                        k, v = kv.split("=")
                        if k == "max_drones":
                            capacity = int(v)
                        elif k == "zone":
                            zone_type = v
                if line.startswith("start_hub"):
                    capacity = 10 ** 9
                    start_name = name
                elif line.startswith("end_hub"):
                    capacity = 10 ** 9
                    end_name = name
                zones[name] = {"capacity": capacity, "zone_type": zone_type}

            elif line.startswith("connection"):
                parts = line.split()
                a, b = parts[1].split("-")
                cap = 1
                if "[" in line:
                    inside = line[line.find("[") + 1:line.find("]")]
                    k, v = inside.split("=")
                    if k == "max_link_capacity":
                        cap = int(v)
                key = frozenset((a, b))
                connections.add(key)
                conn_capacity[key] = cap

    if start_name is None or end_name is None or nb_drones is None:
        raise MapError("map missing start_hub/end_hub/nb_drones")

    return zones, connections, conn_capacity, start_name, end_name, nb_drones


def parse_output_line(line):
    """Return list of (drone_id, from_zone_or_None, to_zone) for one turn."""
    moves = []
    for token in line.strip().split():
        parts = token.split("-")
        drone_id = parts[0]
        if len(parts) == 2:
            moves.append((drone_id, None, parts[1]))
        elif len(parts) == 3:
            moves.append((drone_id, parts[1], parts[2]))
        else:
            raise MapError(f"unparseable token: {token}")
    return moves


def main():
    if len(sys.argv) < 3:
        print("usage: python3 validate.py <map_file> <output_file|->")
        sys.exit(1)

    map_path = sys.argv[1]
    out_path = sys.argv[2]

    zones, connections, conn_capacity, start_name, end_name, nb_drones = parse_map(map_path)

    if out_path == "-":
        lines = sys.stdin.readlines()
    else:
        with open(out_path) as f:
            lines = f.readlines()
    lines = [l for l in lines if l.strip()]

    position = {f"D{i+1}": start_name for i in range(nb_drones)}
    errors = []
    warnings = []

    for turn_idx, line in enumerate(lines, start=1):
        try:
            moves = parse_output_line(line)
        except MapError as e:
            errors.append(f"turn {turn_idx}: {e}")
            continue

        zone_occupants = defaultdict(set)
        conn_usage = defaultdict(int)

        seen_this_turn = set()
        for drone_id, from_zone, to_zone in moves:
            seen_this_turn.add(drone_id)
            prev = position.get(drone_id)
            if from_zone is not None and prev is not None and from_zone != prev:
                warnings.append(
                    f"turn {turn_idx}: {drone_id} printed from={from_zone} "
                    f"but tracked position was {prev}"
                )
            real_from = from_zone if from_zone is not None else prev

            # A 2-part token where to_zone equals the drone's already-tracked
            # position is just the "arrival confirmation" print for a
            # restricted-zone transit that started on a previous turn (see
            # run()'s transit_output logic) — not an actual new hop. Skip
            # connection checks for it.
            is_arrival_confirmation = (from_zone is None and to_zone == prev)

            if real_from is not None and not is_arrival_confirmation:
                key = frozenset((real_from, to_zone))
                if key not in connections:
                    errors.append(
                        f"turn {turn_idx}: {drone_id} moved {real_from} -> {to_zone} "
                        f"but no such connection exists in the map"
                    )
                else:
                    conn_usage[key] += 1

            if to_zone not in zones:
                errors.append(f"turn {turn_idx}: {drone_id} moved to unknown zone {to_zone}")
            else:
                if zones[to_zone]["zone_type"] == "blocked":
                    errors.append(f"turn {turn_idx}: {drone_id} entered blocked zone {to_zone}")

            position[drone_id] = to_zone

        # every drone not mentioned this turn keeps its previous position
        for drone_id, pos in position.items():
            zone_occupants[pos].add(drone_id)

        # check zone capacity
        for zone_name, occupants in zone_occupants.items():
            cap = zones.get(zone_name, {}).get("capacity")
            if cap is not None and len(occupants) > cap:
                errors.append(
                    f"turn {turn_idx}: zone '{zone_name}' has {len(occupants)} drones "
                    f"(occupants: {sorted(occupants)}) but capacity is {cap}"
                )

        # check connection capacity (same-turn crossings only — see docstring)
        for key, count in conn_usage.items():
            cap = conn_capacity.get(key, 1)
            if count > cap:
                a, b = tuple(key)
                errors.append(
                    f"turn {turn_idx}: connection {a}-{b} had {count} drones cross "
                    f"simultaneously but max_link_capacity is {cap}"
                )

    total_turns = len(lines)
    not_finished = [d for d, pos in position.items() if pos != end_name]

    print(f"Parsed {total_turns} turns for {nb_drones} drones.")
    if not_finished:
        errors.append(
            f"{len(not_finished)} drone(s) never reached '{end_name}': {sorted(not_finished)}"
        )
    else:
        print(f"All {nb_drones} drones reached '{end_name}'.")

    if warnings:
        print(f"\n{len(warnings)} WARNING(S):")
        for w in warnings[:20]:
            print(f"  ! {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")

    if errors:
        print(f"\n{len(errors)} VIOLATION(S) FOUND:")
        for e in errors[:30]:
            print(f"  X {e}")
        if len(errors) > 30:
            print(f"  ... and {len(errors) - 30} more")
        sys.exit(1)
    else:
        print("\nNo capacity or connectivity violations found (see limitation note in file header).")
        sys.exit(0)


if __name__ == "__main__":
    main()
