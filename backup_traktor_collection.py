#!/usr/bin/env python3
"""
Backup automatico della Traktor collection prima dei test.
Evita perdita dati durante esperimenti vision-guided.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
import os
import shutil
from datetime import datetime
from pathlib import Path


def find_traktor_collection():
    """
    Trova il file collection.nml di Traktor.

    Percorsi Windows standard:
    - Documents/Native Instruments/Traktor 3.x/collection.nml
    - %APPDATA%/Native Instruments/Traktor 3.x/collection.nml

    Returns:
        Path: Percorso al file collection.nml o None se non trovato
    """
    possible_paths = [
        Path.home() / "Documents" / "Native Instruments",
        Path(os.getenv("APPDATA", "")) / "Native Instruments"
    ]

    for base_path in possible_paths:
        if base_path.exists():
            # Cerca cartelle Traktor 3.x
            for item in base_path.iterdir():
                if item.is_dir() and item.name.startswith("Traktor"):
                    collection = item / "collection.nml"
                    if collection.exists():
                        return collection
    return None


def backup_collection(dry_run=False):
    """
    Esegue backup della collection con timestamp.

    Args:
        dry_run: Se True, simula il backup senza copiare

    Returns:
        bool: True se successo, False altrimenti
    """
    collection_path = find_traktor_collection()

    if not collection_path:
        print("[ERROR] Collection.nml NON TROVATO!")
        print("Verifica manualmente il percorso:")
        print("  - Documents/Native Instruments/Traktor X.X/")
        print("  - %APPDATA%/Native Instruments/Traktor X.X/")
        return False

    # Crea cartella backup
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Nome con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"collection_backup_{timestamp}.nml"

    if dry_run:
        print("[DRY-RUN] Simulazione backup:")
        print(f"  FROM: {collection_path}")
        print(f"  TO:   {backup_path}")
        size_mb = collection_path.stat().st_size / (1024*1024)
        print(f"  SIZE: {size_mb:.2f} MB")
        return True

    # Copia effettiva
    try:
        shutil.copy2(collection_path, backup_path)
        size_mb = backup_path.stat().st_size / (1024*1024)
        print("[OK] BACKUP COMPLETATO!")
        print(f"   Original: {collection_path}")
        print(f"   Backup:   {backup_path}")
        print(f"   Size:     {size_mb:.2f} MB")
        return True
    except Exception as e:
        print(f"[ERROR] Errore durante backup: {e}")
        return False


def main():
    """Main entry point."""
    import sys

    dry_run = "--dry-run" in sys.argv

    print("=" * 70)
    print("TRAKTOR COLLECTION BACKUP")
    print("=" * 70)
    print()

    success = backup_collection(dry_run=dry_run)

    print()
    if success and not dry_run:
        print("[OK] Puoi procedere con i test in sicurezza!")
        print()
        print("Backup salvato in: data/backups/")
        print("In caso di problemi, copia il backup nella cartella Traktor originale.")
    elif success and dry_run:
        print("[OK] Dry-run OK! Rimuovi --dry-run per backup reale")
    else:
        print("[ERROR] Risolvi i problemi prima di procedere!")
        sys.exit(1)


if __name__ == "__main__":
    main()
