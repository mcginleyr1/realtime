#Main files
SITE_FILE = 'javascript/dashboard.js'
SITE_SERVICES = 'services'

#File lists
EXTERNALS = FileList.new('extern/closure-library/**/*.js')
JAVASCRIPT = FileList.new('javascript/**/*.js').exclude('dashboard.js')
TEMPLATES = FileList.new('templates/**/*.soy')
BUILT_TEMPLATES = FileList.new('build/templates/**/*')

#Roots
EXTERNS = 'extern/closure-library/'
JS = 'javascript'

#Compilers
SOY_COMPILER = 'tools/soy-compiler/SoyToJsSrcCompiler.jar'
CLOSURE_BUILDER = 'tools/closure-builder/build/closurebuilder.py'
CLOSURE_COMPILER = 'tools/closure-compiler/compiler.jar'

#Build dirs
BUILD_TEMPLATES = 'build/templates/'
SITE_OUTPUT = 'build/dashboard.js'


##Tasks
desc "Compile the soy templates"
task :compile_soy do
  command = "java -jar #{SOY_COMPILER} #{TEMPLATES.to_s} \
      --outputPathFormat #{BUILD_TEMPLATES}{INPUT_FILE_NAME_NO_EXT}.js \
      --shouldGenerateJsdoc \
      --shouldProvideRequireSoyNamespaces \
      --shouldDeclareTopLevelNamespaces"
  sh command
end

desc "Compile the site javascript."
task :compile_site => [:compile_soy] do
    inputs = JAVASCRIPT.map{|x| "-i #{x} "}.compact
    built_templates = BUILT_TEMPLATES.map{|x| "-i #{x} "}.compact
    command = "#{CLOSURE_BUILDER} \
      --i #{SITE_FILE} \
        #{inputs} #{built_templates} \
      --root #{EXTERNS} \
      --root #{JS} \
      --root #{BUILD_TEMPLATES} \
      --output_mode=compiled \
      --output_file=#{SITE_OUTPUT} -c #{CLOSURE_COMPILER} \
      --compiler_flags='--compilation_level=WHITESPACE_ONLY' \
      --compiler_flags=\"--js_output_file='#{SITE_OUTPUT}'\""
    sh command
end

desc "Run the unit tests."
task :build=> [:compile_site] do
    puts "BUILT"
end

desc "Run the unit tests."
task :test => [:compile_site] do
    sh 'sh services/testrunner.sh'
end
