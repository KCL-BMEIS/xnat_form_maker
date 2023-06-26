/*
 * xnat-workshop: org.apache.turbine.app.xnat.modules.screens.XDATScreen_edit_workshop_biosampleCollection
 * XNAT http://www.xnat.org
 * Copyright (c) 2017, Washington University School of Medicine
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.apache.turbine.app.xnat.modules.screens;

import org.apache.turbine.util.RunData;
import org.apache.velocity.context.Context;
import org.nrg.xdat.XDAT;
import org.nrg.xdat.om.[OM_NAME];
import org.nrg.xdat.om.XnatSubjectassessordata;
import org.nrg.xdat.om.XnatSubjectdata;
import org.nrg.xft.XFTItem;
import org.nrg.xft.exception.ElementNotFoundException;
import org.nrg.xft.exception.FieldNotFoundException;
import org.nrg.xft.exception.XFTInitException;
import org.nrg.xnat.turbine.modules.screens.EditSubjectAssessorScreen;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.List;

public class [CLASS_NAME] extends EditSubjectAssessorScreen {
    @Override
    public String getElementName() {
        return [OM_NAME].SCHEMA_ELEMENT_NAME;
    }

    @Override
    public void finalProcessing(RunData data, Context context) {
        super.finalProcessing(data,context);

        try {
            final String subjectId;
            if (!context.containsKey("subjectId")) {
                if (context.containsKey("part")) {
                    final Object part = context.get("part");
                    if (part instanceof XnatSubjectdata) {
                        subjectId = ((XnatSubjectdata) part).getId();
                    } else if (part instanceof XFTItem) {
                        subjectId = ((XFTItem) part).getStringProperty("ID");
                    } else {
                        subjectId = part.toString();
                    }
                    context.put("subjectId", subjectId);
                } else {
                    subjectId = (String) context.get("part_id");
                }
            } else {
                subjectId = (String) context.get("subjectId");
            }

            if (!context.containsKey("label")) {
                final XnatSubjectdata subject    = XnatSubjectdata.getXnatSubjectdatasById(subjectId, XDAT.getUserDetails(), false);
                final List<XnatSubjectassessordata> echos = subject.getExperiments_experiment([OM_NAME].SCHEMA_ELEMENT_NAME);
                final String subjectLabel = subject.getLabel();
                int index = 1;
                String label = null;
                while (label == null) {

                    SimpleDateFormat sdf = new SimpleDateFormat("ddMMyyyy");
                    long timestamp=Calendar.getInstance().getTimeInMillis();

                    final String test = subjectLabel + "_[LABEL_TAG]_" + sdf.format(timestamp) + "_" +String.format("%d", index);
                    boolean matches = false;
                    for (final XnatSubjectassessordata echo : echos) {
                        if (echo.getLabel().equals(test)) {
                            matches = true;
                            index++;
                            break;
                        }
                    }
                    if (!matches) {
                        label = test;
                    }
                }
                context.put("label", label.replaceAll("\"",""));
            }
        } catch (XFTInitException | ElementNotFoundException | FieldNotFoundException e) {
            final String message = "An error occurred trying to get the subject ID when creating assessor.";
            // eek, log out of date....
            //log.error(message, e);
            throw new RuntimeException(message, e);
        }
    }
}
