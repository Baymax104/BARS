"""数据格式化命令；训练、推理与分析仍使用 src.main。"""

import argparse
import json
import logging
from pathlib import Path

from omegaconf import OmegaConf

from src.data.preparation import PreparationConfig, prepare_dataset


def load_config(path: str, overrides: list[str]) -> PreparationConfig:
    cfg = OmegaConf.load(path)
    valid = set(PreparationConfig.__dataclass_fields__)
    for override in overrides:
        key, separator, _ = override.partition("=")
        if not separator or key not in valid:
            raise ValueError(f"Unknown or invalid preparation override: {override}")
    cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(overrides))
    return PreparationConfig(**OmegaConf.to_container(cfg, resolve=True))


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="离线准备标准数据文件，不运行模型。")
    parser.add_argument("--config", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-records", type=int, default=500000, help="dry-run 每份源文件最多读取的记录数")
    parser.add_argument("--report", help="可选验证回执路径，必须位于源目录和正式输出目录之外")
    parser.add_argument("overrides", nargs="*", help="已声明的 key=value 配置覆盖")
    args = parser.parse_args(argv)
    try:
        cfg = load_config(args.config, args.overrides)
        report = Path(args.report).resolve() if args.report else None
        if report:
            for protected in (Path(cfg.source_dir).resolve(), Path(cfg.output_dir).resolve()):
                if report == protected or protected in report.parents:
                    raise ValueError("Report must stay outside source and formal output directories.")
            if report.exists():
                raise FileExistsError(f"Refusing to overwrite report: {report}")
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        manifest = prepare_dataset(cfg, dry_run=args.dry_run, max_records=args.max_records)
        if report:
            report.parent.mkdir(parents=True, exist_ok=True)
            with report.open("x", encoding="utf-8") as handle:
                json.dump(manifest, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
        print(
            json.dumps(
                {
                    "dataset": manifest["dataset"],
                    "scope": manifest["scope"],
                    "protocol": manifest["protocol"],
                    "counts": manifest["counts"],
                    "validation": manifest["validation"],
                    "report": str(report) if report else None,
                },
                ensure_ascii=False,
            )
        )
    except (ValueError, OSError, TypeError) as error:
        parser.exit(2, f"数据准备失败：{error}\n")


if __name__ == "__main__":
    main()
