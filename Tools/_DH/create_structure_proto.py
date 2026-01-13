import os

ROOT = os.path.join("Resources", "Prototypes")
TARGET_FORK = "_DH"
PLACEHOLDER = "file.txt"

def should_copy_dir(path: str, root: str) -> bool:
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)

    # если любой сегмент пути начинается с "_" — игнорируем
    return not any(p.startswith("_") for p in parts)

def main():
    root_abs = os.path.abspath(ROOT)
    target_root = os.path.join(root_abs, TARGET_FORK)

    os.makedirs(target_root, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_abs):
        if not should_copy_dir(dirpath, root_abs):
            dirnames[:] = []
            continue

        rel_path = os.path.relpath(dirpath, root_abs)
        if rel_path == ".":
            continue

        target_dir = os.path.join(target_root, rel_path)
        os.makedirs(target_dir, exist_ok=True)

        placeholder = os.path.join(target_dir, PLACEHOLDER)
        if not os.path.exists(placeholder):
            with open(placeholder, "w", encoding="utf-8") as f:
                f.write("# Файл создан для структуры проекта Dark Haven, можете его удалить если создаёте рядом .yml файл\n")

        print(f"[OK] _DH/{rel_path}")

    print("\nГотово: структура полностью воссоздана в _DH")

if __name__ == "__main__":
    main()

"""
    ╔════════════════════════════════════════════╗
    ║   Schrödinger's Cat Code   🐾              ║
    ║   Автор: Шрёдька (Discord: schrodinger71)   ║
    ║   Лицензия: AGPL v3.0                       ║
    ║   /\_/\\                                    ║
    ║  ( o.o )  Meow!                             ║
    ║   > ^ <                                     ║
    ╚════════════════════════════════════════════╝
"""
