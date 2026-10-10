import json, glob

base = "/media/alamgir-zk/debian13-hdd/alamgir-zk/cluster-ai-training-sets/terminal-training-set-nothinking/part8"
cats = ["107", "108", "109", "110", "111", "112", "113", "114", "115", "116"]
all_files = []
for c in cats:
    all_files.extend(glob.glob(f"{base}/{c}*"))

for f in sorted(all_files):
    try:
        with open(f) as fp:
            data = json.load(fp)
        print(f'{f.split("/")[-1]}: {len(data)} entries - OK')
    except json.JSONDecodeError as e:
        print(f'{f.split("/")[-1]}: ERROR - {e}')
