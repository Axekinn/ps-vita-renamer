#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def setup_logging() -> logging.Logger:
    """Configure le système de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('psvita_renamer.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_csv_data(csv_path: str) -> Dict[str, Dict[str, str]]:
    """
    Charge les données du fichier CSV et les retourne sous forme de dictionnaire.
    
    Args:
        csv_path: Chemin vers le fichier CSV
        
    Returns:
        Dictionnaire avec Media_ID comme clé et les données du jeu
    """
    games_data = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Utiliser Media_ID au lieu de Title_ID
                media_id = row.get('Media_ID', '').strip()
                if media_id:
                    games_data[media_id] = {
                        'title_name': row.get('Title', '').strip(),
                        'version': row.get('Update_Version', '').strip(),
                        'filename': row.get('Update_Filename', '').strip()
                    }
        
        logging.info(f"Chargé {len(games_data)} jeux depuis le CSV")
        return games_data
        
    except FileNotFoundError:
        logging.error(f"Fichier CSV non trouvé: {csv_path}")
        return {}
    except Exception as e:
        logging.error(f"Erreur lors du chargement du CSV: {e}")
        return {}

def clean_title_name(title: str) -> str:
    """
    Nettoie le nom du titre pour qu'il soit valide comme nom de fichier.
    
    Args:
        title: Nom du titre à nettoyer
        
    Returns:
        Nom du titre nettoyé
    """
    # Remplacer les caractères invalides pour les noms de fichiers
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '', title)
    
    # Remplacer les caractères spéciaux par des espaces
    cleaned = re.sub(r'[^\w\s\-\.\(\)\[\]]', ' ', cleaned)
    
    # Supprimer les espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def extract_title_id_from_filename(filename: str) -> Optional[str]:
    """
    Extrait le Title_ID depuis le nom de fichier PKG.
    
    Args:
        filename: Nom du fichier PKG
        
    Returns:
        Title_ID extrait ou None si non trouvé
    """
    # Pattern pour extraire le Title_ID (format PCxx00000)
    pattern = r'-(PC[SABE]\w{5})[_-]'
    match = re.search(pattern, filename)
    
    if match:
        return match.group(1)
    
    # Pattern alternatif si le premier ne fonctionne pas
    pattern2 = r'UP\d+-([A-Z]{4}\d{5})_'
    match2 = re.search(pattern2, filename)
    
    if match2:
        return match2.group(1)
    
    # Pattern pour les fichiers HP (région asiatique)
    pattern3 = r'HP\d+-([A-Z]{4}\d{5})_'
    match3 = re.search(pattern3, filename)
    
    if match3:
        return match3.group(1)
    
    # Pattern pour les fichiers EP (région européenne)
    pattern4 = r'EP\d+-([A-Z]{4}\d{5})_'
    match4 = re.search(pattern4, filename)
    
    if match4:
        return match4.group(1)
    
    # Pattern pour les fichiers JP (région japonaise)
    pattern5 = r'JP\d+-([A-Z]{4}\d{5})_'
    match5 = re.search(pattern5, filename)
    
    if match5:
        return match5.group(1)
    
    return None

def is_correctly_formatted(filename: str) -> bool:
    """
    Vérifie si le fichier est déjà correctement formaté.
    
    Args:
        filename: Nom du fichier à vérifier
        
    Returns:
        True si le fichier est déjà correctement formaté
    """
    pattern = r'.+\s\[UPDATE\s[\d\.]+\]\[[A-Z]{4}\d{5}\]\(axekin\.com\)\.pkg$'
    return bool(re.match(pattern, filename))

def generate_new_filename(title_name: str, version: str, title_id: str) -> str:
    """
    Génère le nouveau nom de fichier selon le format spécifié.
    
    Args:
        title_name: Nom du jeu
        version: Version de la mise à jour
        title_id: ID du titre
        
    Returns:
        Nouveau nom de fichier formaté
    """
    clean_title = clean_title_name(title_name)
    return f"{clean_title} [UPDATE {version}][{title_id}](axekin.com).pkg"

def rename_files(directory_path: str, csv_path: str, dry_run: bool = True) -> Tuple[List[str], List[str]]:
    """
    Renomme les fichiers dans le répertoire selon les données du CSV.
    
    Args:
        directory_path: Chemin du répertoire contenant les fichiers
        csv_path: Chemin vers le fichier CSV
        dry_run: Si True, simule le renommage sans l'effectuer
        
    Returns:
        Tuple contenant les listes des fichiers renommés avec succès et des erreurs
    """
    logger = logging.getLogger(__name__)
    
    # Charger les données du CSV
    games_data = load_csv_data(csv_path)
    if not games_data:
        logger.error("Aucune donnée chargée depuis le CSV")
        return [], ["Aucune donnée chargée depuis le CSV"]
    
    # Vérifier que le répertoire existe
    if not os.path.isdir(directory_path):
        error_msg = f"Répertoire non trouvé: {directory_path}"
        logger.error(error_msg)
        return [], [error_msg]
    
    renamed_files = []
    errors = []
    
    # Parcourir tous les fichiers .pkg dans le répertoire
    for filename in os.listdir(directory_path):
        if not filename.lower().endswith('.pkg'):
            continue
        
        # Vérifier si le fichier est déjà correctement formaté
        if is_correctly_formatted(filename):
            logger.info(f"Fichier déjà correctement formaté: {filename}")
            continue
        
        # Extraire le Title_ID du nom de fichier
        title_id = extract_title_id_from_filename(filename)
        if not title_id:
            error_msg = f"Impossible d'extraire le Title_ID de: {filename}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        # Vérifier si le Title_ID existe dans les données CSV
        if title_id not in games_data:
            error_msg = f"Title_ID {title_id} non trouvé dans le CSV pour: {filename}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        # Récupérer les données du jeu
        game_data = games_data[title_id]
        title_name = game_data['title_name']
        version = game_data['version']
        
        if not title_name or not version:
            error_msg = f"Données manquantes pour {title_id}: titre='{title_name}', version='{version}'"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        # Générer le nouveau nom de fichier
        new_filename = generate_new_filename(title_name, version, title_id)
        
        # Chemins complets
        old_path = os.path.join(directory_path, filename)
        new_path = os.path.join(directory_path, new_filename)
        
        # Vérifier si le fichier de destination existe déjà
        if os.path.exists(new_path):
            error_msg = f"Le fichier de destination existe déjà: {new_filename}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Renommerait: {filename} -> {new_filename}")
                renamed_files.append(f"{filename} -> {new_filename}")
            else:
                os.rename(old_path, new_path)
                logger.info(f"Renommé: {filename} -> {new_filename}")
                renamed_files.append(f"{filename} -> {new_filename}")
                
        except OSError as e:
            error_msg = f"Erreur lors du renommage de {filename}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    return renamed_files, errors

def main():
    """Fonction principale du script."""
    logger = setup_logging()
    
    print("=== Renommeur de fichiers PS Vita ===")
    print()
    
    # Demander les chemins à l'utilisateur
    directory_path = input("Entrez le chemin du répertoire contenant les fichiers .pkg: ").strip()
    csv_path = input("Entrez le chemin du fichier CSV: ").strip()
    
    # Option de simulation
    dry_run_choice = input("Voulez-vous faire une simulation (y/n)? [y]: ").strip().lower()
    dry_run = dry_run_choice != 'n'
    
    if dry_run:
        print("\n=== MODE SIMULATION - Aucun fichier ne sera renommé ===")
    else:
        print("\n=== MODE RÉEL - Les fichiers seront renommés ===")
    
    print()
    
    # Effectuer le renommage
    renamed_files, errors = rename_files(directory_path, csv_path, dry_run)
    
    # Afficher les résultats
    print(f"\n=== RÉSULTATS ===")
    print(f"Fichiers traités avec succès: {len(renamed_files)}")
    print(f"Erreurs rencontrées: {len(errors)}")
    
    if renamed_files:
        print(f"\nFichiers {'qui seraient ' if dry_run else ''}renommés:")
        for rename_info in renamed_files:
            print(f"  - {rename_info}")
    
    if errors:
        print(f"\nErreurs:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"\nLes logs détaillés sont disponibles dans: psvita_renamer.log")

if __name__ == "__main__":
    main()