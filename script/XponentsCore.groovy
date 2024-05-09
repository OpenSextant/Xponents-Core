
import org.opensextant.examples.*
import org.opensextant.extractors.test.*

static void usage(){
  println "Xponents help          -- this help message."
  println "Xponents <TEST> <ARGS....>"
  println ""
  println "  each TEST has different contextual ARGS for command line usage."
  println "  these are all demonstrational tests."
  println ""
  println "XponentsCore <TEST> --help | -h  -- displays help on that command, if available."
  println ""
  menu()
  System.exit(-1)
}

static void menu(){  

   println '''Tests available for basic tests or adhoc interaction 
   ======================
      xcoord     -- XCoord coordinate extraction tests
      poli       -- Pattern-based extraction
      xtemp      -- Temporal extraction tests
      =======================
     '''
}


static void main(String[] args){

  def test 
  def app
  if (args.length < 2) {
    usage()
  }
  test = args[0]

  switch(test) {
      case 'xcoord':
        app = new TestXCoord()
         
        //-u input
        //-f tests
        //-t input-lines
        break;
      
      case 'poli':
        app = new TestPoLi()
        // -c cfg -u userinput
        // or 
        // -f 
        break;    
      case 'xtemp':
        app = new TestXTemporal()
        // -f 
        // OR 
        // file
        break;
      default:
        usage();
  }
  args_len=args.length-1
  app.main(args[1..args_len] as String[])
}
