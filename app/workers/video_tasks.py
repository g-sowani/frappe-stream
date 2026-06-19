import subprocess, os, json
from dataclasses import dataclass
from typing import List

@dataclass
class VideoMetadata:
    duration: float
    width: int
    height: int
    fps: float

class FFmpegError(Exception):
    pass

class FFmpegService:
    
    QUALITY_LADDER = [
        {"height": 240,  "video_bitrate": "400k",  "audio_bitrate": "64k",  "bandwidth": 500000},
        {"height": 480,  "video_bitrate": "1200k", "audio_bitrate": "128k", "bandwidth": 1400000},
        {"height": 720,  "video_bitrate": "2500k", "audio_bitrate": "128k", "bandwidth": 2700000},
    ]
    
    def probe(self, input_path: str) -> VideoMetadata:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_streams", "-show_format",
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise FFmpegError(f"ffprobe failed: {result.stderr}")
        
        data = json.loads(result.stdout)
        video_stream = next(
            s for s in data["streams"] if s["codec_type"] == "video"
        )
        
        fps_parts = video_stream["r_frame_rate"].split("/")
        fps = float(fps_parts[0]) / float(fps_parts[1])
        
        return VideoMetadata(
            duration=float(data["format"]["duration"]),
            width=int(video_stream["width"]),
            height=int(video_stream["height"]),
            fps=fps
        )
    
    def generate_thumbnail(self, input_path: str, output_path: str, timestamp: int = 5):
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", input_path,
            "-vframes", "1",
            "-vf", "scale=640:-2",
            "-q:v", "2",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise FFmpegError(f"Thumbnail failed: {result.stderr}")
    
    def transcode_to_hls(self, input_path: str, output_dir: str, quality: dict):
        height = quality["height"]
        quality_dir = f"{output_dir}/{height}p"
        os.makedirs(quality_dir, exist_ok=True)
        
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale=-2:{height}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-b:v", quality["video_bitrate"],
            "-maxrate", quality["video_bitrate"],
            "-bufsize", str(int(quality["video_bitrate"][:-1]) * 2) + "k",
            "-c:a", "aac",
            "-b:a", quality["audio_bitrate"],
            "-hls_time", "6",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", f"{quality_dir}/seg%04d.ts",
            "-hls_flags", "independent_segments",
            f"{quality_dir}/playlist.m3u8"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode != 0:
            raise FFmpegError(f"Transcode {height}p failed: {result.stderr}")
        
        return f"{quality_dir}/playlist.m3u8"
    
    def write_master_manifest(self, output_dir: str, available_qualities: List[int]):
        lines = ["#EXTM3U", "#EXT-X-VERSION:3", ""]
        
        for q in self.QUALITY_LADDER:
            if q["height"] in available_qualities:
                lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={q["bandwidth"]},RESOLUTION={self._res(q["height"])},CODECS="avc1.42e01e,mp4a.40.2"')
                lines.append(f'{q["height"]}p/playlist.m3u8')
                lines.append("")
        
        with open(f"{output_dir}/master.m3u8", "w") as f:
            f.write("\n".join(lines))
    
    def _res(self, height: int) -> str:
        resolutions = {240: "426x240", 480: "854x480", 720: "1280x720", 1080: "1920x1080"}
        return resolutions.get(height, f"?x{height}")
