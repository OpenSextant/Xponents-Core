import org.opensextant.data.Geocoding;
import org.opensextant.extraction.TextMatch;
import org.opensextant.extractors.xcoord.GeocoordMatch;
import org.opensextant.output.AbstractFormatter;
import org.opensextant.output.FormatterFactory;
import org.opensextant.output.MatchInterpreter;
import org.opensextant.processing.Parameters;
import org.opensextant.processing.ProcessingException;

public class TestGISOutputters {

    static class TestInterpreter implements MatchInterpreter {

        TestInterpreter(){

        }
        @Override
        public Geocoding getGeocoding(TextMatch m) {
            return new GeocoordMatch(-1, -1);
        }
    }

    public static void testFormatter() throws ProcessingException {
        AbstractFormatter formatter = (AbstractFormatter) FormatterFactory.getInstance("Shapefile");
        Parameters plist = new Parameters();
        plist.outputDir = "test_output";
        plist.outputFile = "test.shp";
        plist.setJobName("Test Shapes");
        formatter.setParameters(plist);
        formatter.setOutputFilename("test.shp");//plist.getJobName() + formatter.outputExtension);
        formatter.setMatchInterpeter(new TestInterpreter());
        formatter.start(plist.getJobName());
        formatter.finish();
    }

    public static void main(String[] args) {

        try {
            testFormatter();
        } catch (Exception err) {
            err.printStackTrace();
            //System.out.printf(err.getMessage());
        }
    }
}
