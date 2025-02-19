# Using `renv` with `RWrapR`

`RWrapR` will automatically install the required R packages, using the
global library path. Sometimes this is not desirable, and you may want to
use the `renv` package to manage your `R` dependencies. To do this, you can
use `renv` via the `rwrapr` package.

```
import rwrapr as wr

renv = wr.library("renv")
renv.init() # initialize renv
renv.install("statisticsnorway/ssb-metodebiblioteket")
renv.install("metodebiblioteket")

renv.snapshot(type="all") # update lock-file
```

It is important that you use `renv.snapshot(type="all")` to update the lock-file.
Or set `type="packages"` in the renv settings.

```
renv.script("renv::settings$record.type("packages")")
```
This will ensure that all the installed packages are saved in the lock-file. `renv`
usually just looks in the `DESCRIPTION` file, and the `.R` files for package dependencies,
and will not look in for `R` dependencies in `.py` files.

You should also add this to the start of your notebooks to activate the `renv` environment.

```
import rwrarp as wr
renv = wr.library("renv")
renv.autoload()
```

For a more comprehensive guide on using `renv` see [DaplaManualen](https://manual.dapla.ssb.no/statistikkere/renv.html)
