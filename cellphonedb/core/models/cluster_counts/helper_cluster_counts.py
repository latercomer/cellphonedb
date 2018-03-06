import itertools

import pandas as pd

from cellphonedb.core.models.cluster_counts.filter_cluster_counts import filter_empty_cluster_counts
from cellphonedb.core.models.complex import complex_helper


def merge_complex_cluster_counts(clusters_names: pd.DataFrame, complex_counts_composition: pd.DataFrame,
                                 complex_expanded: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the counts values of multiple components of complex.
    Sets the minimum cluster value for the components of a complex.
    """

    def set_complex_cluster_counts(row):
        scores_complex = complex_counts_composition[
            row['complex_multidata_id'] == complex_counts_composition['complex_multidata_id']]

        for cluster_name in clusters_names:
            row[cluster_name] = scores_complex[cluster_name].min()
        return row

    complex_counts = complex_counts_composition.drop_duplicates(['complex_multidata_id'])
    complex_counts = complex_counts.apply(set_complex_cluster_counts, axis=1)
    complex_counts = complex_counts[list(clusters_names) + list(complex_expanded.columns.values)]
    complex_counts = filter_empty_cluster_counts(complex_counts, clusters_names)
    return complex_counts


def get_cluster_combinations(cluster_names):
    return list(itertools.product(cluster_names, repeat=2))


def get_complex_involved_in_counts(multidatas_counts: pd.DataFrame, clusters_names: list,
                                   complex_composition: pd.DataFrame,
                                   complex_expanded: pd.DataFrame) -> pd.DataFrame:
    """
    Gets complexes involved in counts
    """
    print('Finding Complexes')
    complex_counts_composition = complex_helper.get_involved_complex_from_protein(multidatas_counts, complex_expanded,
                                                                                  complex_composition,
                                                                                  drop_duplicates=False)

    complex_counts = merge_complex_cluster_counts(clusters_names, complex_counts_composition, complex_expanded)

    complex_counts['is_complex'] = True

    return complex_counts


def apply_threshold(cluster_counts: pd.DataFrame, cluster_names: list, threshold: float) -> pd.DataFrame:
    """
    Sets to 0 minor value colunts than threshold
    """

    print('Aplicating Threshold {}'.format(threshold))
    cluster_counts_filtered = cluster_counts.copy()
    for cluster_name in cluster_names:
        cluster_counts_filtered.loc[
            cluster_counts_filtered[cluster_name] < float(threshold), [cluster_name]] = 0.0

    return cluster_counts_filtered