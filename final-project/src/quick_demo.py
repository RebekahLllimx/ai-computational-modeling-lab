"""Small deterministic smoke run; does not regenerate the paper figures."""

from ca_model import HobbesCA


for name, penalty, start in (("state of nature", 0.0, None), ("Leviathan", 0.3, 10)):
    model = HobbesCA(grid_size=20, b=1.4, p=penalty, leviathan_time=start, seed=42)
    model.run(20, track_metrics=False)
    metrics = model.get_metrics()
    print(f"{name}: f_c={metrics.f_c:.3f}, clusters={metrics.n_clusters}, "
          f"largest_cluster_share={metrics.a_max:.3f}")
