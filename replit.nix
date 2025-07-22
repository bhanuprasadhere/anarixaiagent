{ pkgs }: {
  deps = [
    # Python and pip
    pkgs.python310
    pkgs.python310Packages.pip

    # Other packages needed for matplotlib
    pkgs.cairo
    pkgs.ffmpeg-full
    pkgs.freetype
    pkgs.ghostscript
    pkgs.glibcLocales
    pkgs.gobject-introspection
    pkgs.gtk3
    pkgs.libxcrypt
    pkgs.pkg-config
    pkgs.qhull
    pkgs.tcl
    pkgs.tk
  ];
  env = {
    # Explicitly set Python and PIP paths (optional but can help with pathing issues)
    PYTHON_BIN = "${pkgs.python310}/bin/python3.10";
    PIP_BIN = "${pkgs.python310Packages.pip}/bin/pip3.10";
  };
}