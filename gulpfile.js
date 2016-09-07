let gulp = require('gulp');
let scss = require('gulp-scss');
let sass = require('gulp-sass');


gulp.task('sass', () => {
  return gulp.src("style/**/*.scss")
  .pipe(sass().on('error', sass.logError))
  .pipe(gulp.dest('style/css/'))
});

gulp.task('sass:watch', () => {
  gulp.watch("style/scss/**/*.scss", ['sass']);
  gulp.watch("*.js", ['sass']);
});

gulp.task('scss', () => {
  gulp.src(
    "style/scss/**/*.scss"
    )
    .pipe(scss(
      {"bundleExec": true}
    ))
    .pipe(gulp.dest("style/css"));
});

// gulp.task('default', ['watch', 'scss', 'serve']);
gulp.task('default', ['sass:watch', 'sass']);

