import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, PROJECT_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


homophily = load_module("homophily", "homophily.py")
evolution = load_module("network_evolution", "network_evolution.py")


class FacebookHomophilyTests(unittest.TestCase):
    def test_ego_vector_and_missing_features_match_recorded_method(self):
        with tempfile.TemporaryDirectory() as temp:
            data = Path(temp)
            (data / "0.featnames").write_text("0 gender;anonymized_A\n1 gender;anonymized_B\n")
            (data / "0.egofeat").write_text("1 0\n")
            (data / "0.feat").write_text("1 1 0\n2 0 1\n3 0 0\n4 0 1\n")
            (data / "0.edges").write_text("1 2\n2 3\n")

            result = homophily.analyze_ego_network(data, 0)
            self.assertEqual(result.known_nodes, 4)
            self.assertEqual(result.valid_edges, 4)
            self.assertAlmostEqual(result.observed, 0.25)
            self.assertAlmostEqual(result.expected, 0.5)
            self.assertAlmostEqual(result.excess, -0.25)

    def test_missing_gender_dimensions_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "0.featnames"
            path.write_text("0 education;school\n")
            with self.assertRaises(ValueError):
                homophily.gender_feature_indices(path)


class NetworkEvolutionTests(unittest.TestCase):
    def test_modularity_uses_the_degree_based_null_model(self):
        model = evolution.NetworkEvolution()
        result = model.calculate_homophily_measures()
        self.assertAlmostEqual(result["simple_homophily"], 0.4)
        self.assertAlmostEqual(result["modularity_q"], 0.01)
        self.assertAlmostEqual(result["original_score"], 0.275)

    def test_recorded_sequential_evolution_reaches_fixed_point(self):
        model = evolution.NetworkEvolution()
        changes = []
        for _ in range(5):
            friendships = model.closure_mechanism_1() + model.closure_mechanism_2()
            memberships = model.closure_mechanism_3()
            changes.append((len(friendships), len(memberships)))
        self.assertEqual(changes, [(2, 2), (1, 1), (0, 2), (0, 1), (0, 0)])
        result = model.calculate_homophily_measures()
        self.assertAlmostEqual(result["simple_homophily"], 11 / 13)
        self.assertAlmostEqual(result["modularity_q"], 0.2721893491)

    def test_synchronous_rules_match_this_recorded_trajectory(self):
        sequential = evolution.NetworkEvolution()
        synchronous = evolution.NetworkEvolution()
        for _ in range(5):
            sequential.closure_mechanism_1()
            sequential.closure_mechanism_2()
            sequential.closure_mechanism_3()

            before = copy.deepcopy(synchronous)
            new_edges = [
                (i, j)
                for i in range(before.num_people)
                for j in range(i + 1, before.num_people)
                if before.social_network[i, j] == 0
                and (before.get_common_friends(i, j) >= before.friendship_threshold
                     or before.get_common_clubs(i, j) >= before.club_friendship_threshold)
            ]
            new_memberships = [
                (i, club)
                for i in range(before.num_people)
                for club in range(before.num_clubs)
                if before.club_affiliations[i, club] == 0
                and before.get_friends_in_club(i, club) >= before.club_participation_threshold
            ]
            for i, j in new_edges:
                synchronous.social_network[i, j] = synchronous.social_network[j, i] = 1
            for i, club in new_memberships:
                synchronous.club_affiliations[i, club] = 1
            self.assertTrue((sequential.social_network == synchronous.social_network).all())
            self.assertTrue((sequential.club_affiliations == synchronous.club_affiliations).all())


if __name__ == "__main__":
    unittest.main()
