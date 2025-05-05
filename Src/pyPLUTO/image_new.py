class Image_new:
    """Class that creates a new figure and sets the LaTeX
    conditions, as well as the matplotlib style.
    Every Image is associated to a figure object and only one in order to
    avoid confusion between images and figures. If you want to create multiple
    figures, you have to create multiple Image objects.

    Returns
    -------
    - None

    Parameters
    ----------
    - close: bool, default True
        If True, the existing figure with the same window number is closed.
    - fig: Figure | None, default None
        The the figure instance. If not None, the figure is used (only
        if we need to associate an Image to an existing figure).
    - figsize: list[float], default [8,5]
        The figure size.
    - fontsize: int, default 17
        The font size.
    - LaTeX: bool | str, default False
        The LaTeX option. Is True is selected, the default LaTeX font
        is used. If 'pgf' is selected, the pgf backend is used to save pdf
        figures with minimal file size. If XeLaTeX is not installed and the
        'pgf' option is selected, the LaTeX option True is used as backup
        strategy.
    - numcolor: int, default 10
        The number of colors in the colorscheme. The default number is 10, but
        the full list contains 24 colors (+ black or white).
    - nwin: int, default 1
        The window number.
    - oldcolor: bool, default False
        if True, the old colors are used
    - style: str, default 'default'
        The style of the figure. Possible values are: 'seaborn', 'ggplot',
        'fivethirtyeight', 'bmh', 'grayscale', 'dark_background', 'classic',
        etc.
    - suptitle: str, default None
        The super title of the figure.
    - suptitlesize: str | int, default 'large'
        The figure title size.
    - tight: bool, default True
        If True, the tight layout is used.
    - withblack: bool, default False
        If True, the black color is used as first color.
    - withwhite: bool, default False
        If True, the white color is used as first color.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: create an empty image

        >>> import pyPLUTO as pp
        >>> I = pp.Image()

    - Example #2: create an image with the pgf backend

        >>> import pyPLUTO as pp
        >>> I = pp.Image(LaTeX = 'pgf')

    - Example #3: create an image with the LaTeX option True

        >>> import pyPLUTO as pp
        >>> I = pp.Image(LaTeX = True)

    - Example #4: create an image with fixed size

        >>> import pyPLUTO as pp
        >>> I = pp.Image(figsize = [5,5])

    - Example #5: create an image with a title

        >>> import pyPLUTO as pp
        >>> I = pp.Image(suptitle = 'Title')

    """

    pass
