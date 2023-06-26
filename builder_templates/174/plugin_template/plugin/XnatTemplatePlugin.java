/*
 * xnat-template: org.nrg.xnat.plugins.template.plugin.XnatTemplatePlugin
 * XNAT http://www.xnat.org
 * Copyright (c) 2017, Washington University School of Medicine
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].plugin;

import org.nrg.dcm.id.CompositeDicomObjectIdentifier;
import org.nrg.dcm.id.FixedProjectSubjectDicomObjectIdentifier;
import org.nrg.framework.annotations.XnatDataModel;
import org.nrg.framework.annotations.XnatPlugin;
[HERE_IMPORT_BEANS]
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.jdbc.core.JdbcTemplate;

@XnatPlugin(value = "[HERE_SCHEMANAME_LOWER]Plugin", 
    name = "XNAT 1.7 [HERE_PLUGIN_NAME] Plugin", 
    entityPackages = "org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].entities",
        dataModels = {
            [HERE_XNAT_DATA_MODELS]
        })
@ComponentScan({"org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].preferences",
                "org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].repositories",
                "org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].rest",
                "org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].services.impl"})
public class Xnat[HERE_SCHEMANAME]Plugin {
    public Xnat[HERE_SCHEMANAME]Plugin() {
        _log.info("Creating the Xnat[HERE_SCHEMANAME]Plugin configuration class");
    }

    @Bean
    public CompositeDicomObjectIdentifier projectXnat02Identifier(final JdbcTemplate template) {
        return new FixedProjectSubjectDicomObjectIdentifier(template, "XNAT_02", "XNAT_02_01");
    }

    @Bean
    public String [HERE_SCHEMANAME_LOWER]PluginMessage() {
        return "This comes from deep within the [HERE_SCHEMANAME_LOWER] plugin.";
    }

    private static final Logger _log = LoggerFactory.getLogger(Xnat[HERE_SCHEMANAME]Plugin.class);
}
