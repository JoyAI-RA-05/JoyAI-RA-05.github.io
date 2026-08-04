# G1 Real-World Demonstrations

These assets support the Demonstrations section of `technical.html`.

- Source archive: `/Users/liwenhao.109/Downloads/G1_desk_final_8_task_videos_20260804.zip`
- Imported: 2026-08-05
- Source format: H.264, YUV 4:2:0, 1280 x 800, 30 fps
- Video processing: copied without transcoding
- Poster processing: extracted at 55% of each video's duration and resized to 640 px wide

Poster generation pattern:

```bash
ffmpeg -ss <duration-times-0.55> -i <video>.mp4 -frames:v 1 \
  -vf "scale=640:-2" -q:v 3 <video>.jpg
```

The filenames are presentation-oriented aliases for the numbered source clips.
