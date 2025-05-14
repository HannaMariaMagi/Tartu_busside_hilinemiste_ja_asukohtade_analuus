import zstandard as zstd
import io
import json
import os

# Sisendfaili tee (.json.zst) – muuda vastavalt oma failile
zst_file_path = "/data/toodeldud_zst_failid/device_194442191_2023-5_job3290626.json.zst"

# Kataloog, kuhu salvestada iga JSON-objekt eraldi failina
output_dir = "näidis_jsonid_cumulocityst"
os.makedirs(output_dir, exist_ok=True)

# Ava ja dekompressi .json.zst fail
with open(zst_file_path, 'rb') as compressed:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(compressed) as reader:
        text_stream = io.TextIOWrapper(reader, encoding='utf-8')

        for i in range(3):  # Võtab esimesed 3 rida
            line = text_stream.readline()
            if not line:
                break
            data = json.loads(line.strip())
            output_path = os.path.join(output_dir, f"json_näide_{i + 1}.json")
            with open(output_path, "w", encoding="utf-8") as out_file:
                json.dump(data, out_file, ensure_ascii=False, indent=4)
            print(f"Salvestatud: {output_path}")