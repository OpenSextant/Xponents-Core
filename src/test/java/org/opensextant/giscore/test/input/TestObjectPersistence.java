/****************************************************************************************
 *  TestObjectPersistence.java
 *
 *  Created: Mar 24, 2009
 *
 *  @author DRAND
 *
 *  (C) Copyright MITRE Corporation 2009
 *
 *  The program is provided "as is" without any warranty express or implied, including
 *  the warranty of non-infringement and the implied warranties of merchantability and
 *  fitness for a particular purpose.  The Copyright owner will not be liable for any
 *  damages suffered by you as a result of using the Program.  In no event will the
 *  Copyright owner be liable for any special, indirect or consequential damages or
 *  lost profits even if the Copyright owner has been advised of the possibility of
 *  their occurrence.
 *
 ***************************************************************************************/
package org.opensextant.giscore.test.input;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.junit.Test;
import org.opensextant.giscore.events.*;
import org.opensextant.giscore.geometry.*;
import org.opensextant.giscore.test.TestGISBase;
import org.opensextant.giscore.utils.Color;
import org.opensextant.giscore.utils.IDataSerializable;
import org.opensextant.giscore.utils.SimpleObjectInputStream;
import org.opensextant.giscore.utils.SimpleObjectOutputStream;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

/**
 * Test the geometry and the feature objects
 *
 * @author DRAND
 */
public class TestObjectPersistence {

// @Test
    public void testSimpleGeometries() throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream(2000);
        SimpleObjectOutputStream soos = new SimpleObjectOutputStream(bos);

        Point p = new Point(.30, .42);
        soos.writeObject(p);

        Point p3d = new Point(30, 42, 200);
        soos.writeObject(p3d);

        Circle c = new Circle(p.getCenter(), 10);
        c.setExtrude(true);
        c.setAltitudeMode("absolute");
        soos.writeObject(c);

        Circle c3d = new Circle(p3d.getCenter(), 10);
        c3d.setTessellate(true);
        soos.writeObject(c3d);

        List<Point> pts = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            pts.add(new Point(i * .01, i * .01));
        }
        Line l = new Line(pts);
        soos.writeObject(l);

        pts = new ArrayList<>();
        pts.add(new Point(.10, .10));
        pts.add(new Point(.10, -.10));
        pts.add(new Point(-.10, -.10));
        pts.add(new Point(-.10, .10));
        pts.add(pts.get(0)); // add first as last
        LinearRing r = new LinearRing(pts);
        soos.writeObject(r);

        soos.close();

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        SimpleObjectInputStream sois = new SimpleObjectInputStream(bis);

        Geometry g = (Geometry) sois.readObject();
        assertEquals(p, g);

        g = (Geometry) sois.readObject();
        assertEquals(p3d, g);

        g = (Geometry) sois.readObject();
        assertEquals(c, g);

        g = (Geometry) sois.readObject();
        assertEquals(c3d, g);

        g = (Geometry) sois.readObject();
        assertEquals(l.getNumPoints(), g.getNumPoints());
        assertEquals(l.getBoundingBox(), g.getBoundingBox());

        g = (Geometry) sois.readObject();
        assertEquals(r.getNumPoints(), g.getNumPoints());
        assertEquals(r.getBoundingBox(), g.getBoundingBox());

        sois.close();
    }

// @Test
    public void testMixedMultiPoint() throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        SimpleObjectOutputStream soos = new SimpleObjectOutputStream(bos);

        Point pt2d = TestGISBase.getRandomPoint();
        Point pt3d = new Point(TestGISBase.random3dGeoPoint());
        List<Point> pts = new ArrayList<>();
        pts.add(pt2d);
        pts.add(pt3d);
        MultiPoint g = new MultiPoint(pts);
        soos.writeObject(g);

        soos.close();

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        SimpleObjectInputStream sois = new SimpleObjectInputStream(bis);

        MultiPoint ml = (MultiPoint) sois.readObject();
        assertEquals(2, ml.getNumParts());
        assertEquals(pt2d, ml.getPart(0));
        assertEquals(pt3d, ml.getPart(1));

        sois.close();
    }

// @Test
    public void testMultiGeometries() throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream(2000);
        SimpleObjectOutputStream soos = new SimpleObjectOutputStream(bos);

        List<Line> lines = new ArrayList<>();
        List<Point> pts = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            pts.add(new Point(i * .01, i * .01));
        }
        Line l = new Line(pts);
        lines.add(l);
        Geometry g = new MultiLine(lines);
        soos.writeObject(g);

        List<LinearRing> rings = new ArrayList<>();
        pts = new ArrayList<>();
        pts.add(new Point(.10, .20));
        pts.add(new Point(.10, .10));
        pts.add(new Point(.20, .10));
        pts.add(new Point(.20, .20));
        pts.add(pts.get(0)); // add first as last
        LinearRing r1 = new LinearRing(pts);
        rings.add(r1);
        g = new MultiLinearRings(rings);
        soos.writeObject(g);

        pts = new ArrayList<>();
        pts.add(new Point(.10, .10));
        pts.add(new Point(.10, -.10));
        pts.add(new Point(-.10, -.10));
        pts.add(new Point(-.10, .10));
        pts.add(pts.get(0)); // add first as last
        LinearRing outer = new LinearRing(pts);
        pts = new ArrayList<>();
        pts.add(new Point(.05, .05));
        pts.add(new Point(.05, -.05));
        pts.add(new Point(-.05, -.05));
        pts.add(new Point(-.05, .05));
        pts.add(pts.get(0)); // add first as last
        List<LinearRing> innerRings = new ArrayList<>();
        innerRings.add(new LinearRing(pts));
        Polygon p = new Polygon(outer, innerRings);
        soos.writeObject(p);

        g = new MultiPolygons(Collections.singletonList(p));
        soos.writeObject(g);

        soos.close();

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        SimpleObjectInputStream sois = new SimpleObjectInputStream(bis);

        MultiLine ml = (MultiLine) sois.readObject();
        assertEquals(1, ml.getNumParts());
        assertEquals(10, ml.getNumPoints());

        MultiLinearRings mlr = (MultiLinearRings) sois.readObject();
        assertEquals(1, mlr.getNumParts());

        Polygon p2 = (Polygon) sois.readObject();
        assertEquals(1, p2.getLinearRings().size());
        assertNotNull(p2.getOuterRing());

        MultiPolygons mp = (MultiPolygons) sois.readObject();
        assertEquals(1, mp.getNumParts());

        sois.close();
    }

// @Test
    public void testFeatureProperties() throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        SimpleObjectOutputStream soos = new SimpleObjectOutputStream(bos);
        List<Line> lines = new ArrayList<>(5);

        // output every combination of extrude and tessellate: 0, 1, or null (2)
        for (int extrude = 0; extrude <= 2; extrude++)
            for (int tessellate = 0; tessellate <= 2; tessellate++) {
                List<Point> pts = new ArrayList<>();
                for (int j = 0; j < 10; j++) {
                    pts.add(new Point(j * .01, j * .01));
                }
                Line l = new Line(pts);
                if (extrude != 2)
                    l.setExtrude(extrude == 1);
                if (tessellate != 2)
                    l.setTessellate(tessellate == 1);
                lines.add(l);
                soos.writeObject(l);
            }

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        SimpleObjectInputStream sois = new SimpleObjectInputStream(bis);

        for (Line line : lines) {
            Geometry g = (Geometry) sois.readObject();
            assertEquals(line.getNumPoints(), g.getNumPoints());
            assertEquals(line.getBoundingBox(), g.getBoundingBox());
            assertEquals(line, g);
            // System.out.println(ToStringBuilder.reflectionToString(g, ToStringStyle.MULTI_LINE_STYLE));
        }
        sois.close();
    }

    /**
     * Only need to test "leaf" classes since the superclasses must participate
     *
     * @throws Exception
     */
// @Test
    public void testFeatures() throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream(2000);
        SimpleObjectOutputStream soos = new SimpleObjectOutputStream(bos);

        Feature pt = makePointFeature();
        soos.writeObject(pt);

        GroundOverlay go = makeGO();
        soos.writeObject(go);

        PhotoOverlay po = makePO();
        soos.writeObject(po);

        ScreenOverlay so = makeSO();
        soos.writeObject(so);

        NetworkLink nl = makeNL();
        soos.writeObject(nl);

        ContainerStart cs = new ContainerStart("folder");
        soos.writeObject(cs);

        Model mo = new Model();
        mo.setLocation(TestGISBase.random3dGeoPoint());
        mo.setAltitudeMode(AltitudeModeEnumType.absolute);
        soos.writeObject(mo);

        soos.close();

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        SimpleObjectInputStream sois = new SimpleObjectInputStream(bis);
        Feature f2 = (Feature) sois.readObject();
        assertEquals(pt, f2);

        GroundOverlay g2 = (GroundOverlay) sois.readObject();
        assertEquals(go, g2);

        PhotoOverlay p2 = (PhotoOverlay) sois.readObject();
        assertEquals(po, p2);

        ScreenOverlay s2 = (ScreenOverlay) sois.readObject();
        assertEquals(so, s2);

        NetworkLink n2 = (NetworkLink) sois.readObject();
        assertEquals(nl, n2);

        ContainerStart c2 = (ContainerStart) sois.readObject();
        assertEquals(cs, c2);

        Model m2 = (Model) sois.readObject();
        assertEquals(mo, m2);
        sois.close();
    }

// @Test
    public void testWrapper() throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream(2000);
        SimpleObjectOutputStream soos = new SimpleObjectOutputStream(bos);
        final int count = 4;
        System.out.println("testWrapper");
        List<IDataSerializable> objects = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            Feature f = makePointFeature();
            f.setName(Integer.toString(i));
            WrappedObject obj = new WrappedObject(f);
            objects.add(obj);
            soos.writeObject(obj);
        }
        soos.close();

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        SimpleObjectInputStream sois = new SimpleObjectInputStream(bis);
        for (IDataSerializable o1 : objects) {
            WrappedObject o2 = (WrappedObject) sois.readObject();
            assertEquals(o1, o2);
        }
        sois.close();
    }

    static Feature makePointFeature() {
        Feature f = new Feature();
        f.setName("test");
        f.setDescription("this is a test placemark");
        Date date = new Date();
        f.setStartTime(date);
        f.setEndTime(date);
        f.setGeometry(new Point(42.504733587704, -71.238861602674));
        return f;
    }

    /**
     * @return
     */
    static NetworkLink makeNL() {
        NetworkLink nl = new NetworkLink();
        nl.setFlyToView(true);
        nl.setLink(new TaggedMap());
        nl.setRefreshVisibility(false);
        return nl;
    }

    /**
     * @return
     */
    static ScreenOverlay makeSO() {
        ScreenOverlay so = new ScreenOverlay();
        ScreenLocation s1 = new ScreenLocation();
        ScreenLocation s2 = new ScreenLocation();
        ScreenLocation s3 = new ScreenLocation();
        ScreenLocation s4 = new ScreenLocation();

        s1.x = 11;
        s1.y = 12;
        s2.x = .3;
        s2.y = .4;
        s2.xunit = ScreenLocation.UNIT.FRACTION;
        s2.yunit = ScreenLocation.UNIT.FRACTION;
        s3.x = 14;
        s3.y = 15;
        s4.x = 16;
        s4.y = 17;
        so.setOverlay(s1);
        so.setRotation(s2);
        so.setSize(s3);
        so.setScreen(s4);
        so.setRotationAngle(.78);

        return so;
    }

    /**
     * @return
     */
    static PhotoOverlay makePO() {
        PhotoOverlay po = new PhotoOverlay();
        po.setColor(Color.RED);
        po.setId("po01");

        return po;
    }

    static GroundOverlay makeGO() throws URISyntaxException {
        GroundOverlay go = new GroundOverlay();
        go.setAltitude(3.1);
        go.setAltitudeMode(AltitudeModeEnumType.clampToGround);
        go.setColor(Color.red);
        go.setDescription("abc");
        go.setDrawOrder(2);
        go.setEast(22.0);
        go.setWest(10.0);
        go.setNorth(42.0);
        go.setSouth(40.0);
        go.setStartTime(new Date(100000));
        go.setEndTime(new Date(110000));
        go.setGeometry(new Point(1.0, 2.0));
        TaggedMap tm = new TaggedMap("extra");
        tm.put("a", "1");
        tm.put("b", "2");
        tm.put("c", "3");
        go.setIcon(tm);
        go.setName("def");
        go.setRotation(-20.0);
        go.setSchema(new URI("#123"));
        go.setStyleUrl("#style1");

        SimpleField f1 = new SimpleField("f1");
        f1.setLength(100);
        go.putData(f1, 5.6);
        return go;
    }
}
