/*
 *
 * Copyright 2012-2013 The MITRE Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.opensextant.extractors.xtemporal;

import org.opensextant.extractors.flexpat.RegexPattern;

/**
 * @author ubaldino
 */
public class DateTimePattern extends RegexPattern {

    /**
     *
     */
    public int family_id = -1;

    /**
     * @param fam
     * @param id
     * @param desc
     */
    public DateTimePattern(String fam, String id, String desc) {
        super(fam, fam + "-" + id, desc);

        family_id = XTConstants.getPatternFamily(family);
    }
}