{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        # arm systems
        "aarch64-darwin"
        "aarch64-linux"

        # x86
        "x86_64-darwin"
        "x86_64-linux"
      ];

      forEachSystem = fn: nixpkgs.lib.genAttrs systems (system: fn
        nixpkgs.legacyPackages.${system});
    in
    {
      devShell = forEachSystem (pkgs:

        pkgs.mkShell {
          packages = [
            (pkgs.python311.withPackages (ps: [ ps.poppler-qt5 ]))
          ];
        }
      );

      formatter = forEachSystem (pkgs: pkgs.nixpkgs-fmt);
    };
}
