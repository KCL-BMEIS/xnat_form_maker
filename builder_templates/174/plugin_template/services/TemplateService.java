/*
 * xnat-template: org.nrg.xnat.plugins.template.services.TemplateService
 * XNAT http://www.xnat.org
 * Copyright (c) 2017, Washington University School of Medicine
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].services;

import org.nrg.framework.orm.hibernate.BaseHibernateService;
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].entities.[HERE_SCHEMANAME];

public interface [HERE_SCHEMANAME]Service extends BaseHibernateService<[HERE_SCHEMANAME]> {
    /**
     * Finds the template with the indicated {@link [HERE_SCHEMANAME]#getTemplateId() template ID}.
     *
     * @param templateId The template ID.
     *
     * @return The template with the indicated ID, null if not found.
     */
    [HERE_SCHEMANAME] findByTemplateId(final String templateId);
}
